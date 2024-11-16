from fastapi import APIRouter,WebSocket

from model.event import Location
from model.websocket import FinishMessage
from repository.distance import Distance
from service.websocket import WebSocketService
from application.notification import SendNotification
from service.fetch_profile import ProfileService
from service.fetch_event import EventService

from typing import List, Dict
from datetime import datetime, timezone
import json


def get_websocket_router(supabase_url: str):
    router = APIRouter(prefix="/ws", tags=["Websocket"])
    websocket_service = WebSocketService(supabase_url)
    distances = Distance(supabase_url)
    notification = SendNotification(supabase_url)
    profile_service = ProfileService(supabase_url)
    event_service = EventService(supabase_url)
        
    @router.websocket("/ranking")
    async def websocket_endpoint(event_id:int,websocket: WebSocket):
        await websocket.accept()
        
        connected_clients: Dict[int, WebSocket] = {}
        user_locations: Dict[int, Location] = {}
        
        event_deadline_time = websocket_service.calculate_deadline(event_id)
        
        try:
            await websocket.send_text(json.dumps({
                "action": "connected",
                "message": "WebSocket connection established"
            }))

            while True:
                now = datetime.now(timezone.utc)

                if now >= event_deadline_time:
                    finish_message = {
                        "action": "tikokulympic_finished",
                        "message": "この遅刻リンピックは終了しました。"
                    }
                    
                    for user_id in connected_clients.keys():
                        event_service.event.add_arrival_time(user_id, now, event_id)
                        aliase_id = profile_service.judge_aliase(user_id)
                        profile_service.profile.update_aliase_id(user_id,aliase_id)
                        notification.send_renew_aliase(user_id)
                    
                    distances.delete_all_distance()
                    
                    for client_websocket in connected_clients.values():
                        client_websocket.send_text(json.dumps(finish_message))
                        client_websocket.close()
                    

                    connected_clients.clear()
                    break

                data = await websocket.receive_text()
                message = json.loads(data)

                if message["action"] == "update_location":
                    user_id = message["user_id"]
                    connected_clients[user_id] = websocket
                    latitude = float(message["latitude"])
                    longitude = float(message["longitude"])
                    
                    user_locations[user_id] = Location(latitude=latitude, longitude=longitude)
                    distance = websocket_service.calculate_distance(event_id, user_locations[user_id])
                    
                    if distances.is_distance_present(user_id) == True:
                        distances.update_distance(distance,user_id)

                    else:
                        distances.insert_distance(distance,user_id)
                        
                    await websocket_service.send_ranking(websocket)

                elif message["action"] == "get_ranking":
                    await websocket_service.send_ranking(websocket)
                    

                elif message["action"] == "arrival_notification":
                    
                    finish_message = FinishMessage(
                        action=message["action"],
                        user_id=message['user_id'],
                        arrival_time=message['arrival_time']
                    )
                    
                    distances.delete_distance(finish_message.user_id)
                    
                    await websocket_service.send_ranking(websocket)
                    
                    event_service.event.add_arrival_time(finish_message.user_id, finish_message.arrival_time, event_id)
                    
                    aliase_id = profile_service.judge_aliase(finish_message.user_id)
                    profile_service.profile.update_aliase_id(finish_message.user_id,aliase_id)
                    notification.send_renew_aliase(finish_message.user_id)
                    
                    print("success")
                    

        except Exception as e:
            print(f"WebSocket error: {e}")
            
    return router