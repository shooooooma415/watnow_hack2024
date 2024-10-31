from fastapi import FastAPI,WebSocket,Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from model.event import Location,EventID
from model.attendances import Attendances,AttendancesResponse
from model.websocket import FinishMessage
from repository.event import Event
from repository.distance import Distance
from repository.add_votes import AddVotes
from repository.get_attendance import GetAttendance
from repository.profile import Profile
from service.fetch_event import EventService
from service.websocket import WebSocketService
from service.fetch_profile import ProfileService
from service.vote import Vote
import os
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime,timezone
import json

# ルーターの呼び出し
from routers.auth import get_auth_router
from routers.event import get_event_router
from routers.user import get_users_router

load_dotenv()

app = FastAPI()
supabase_url = os.getenv('SUPABASE_URL')

engine = create_engine(supabase_url)
event = Event(supabase_url)
event_service = EventService(supabase_url)
websocket_service = WebSocketService(supabase_url)
profile_service = ProfileService(supabase_url)
distances = Distance(supabase_url)
vote = Vote(supabase_url)
add_votes = AddVotes(supabase_url)
get_attendance = GetAttendance(supabase_url)
profile = Profile(supabase_url)

today_event_id_list: List[int] = []


# ルーターの取得
auth_router = get_auth_router(supabase_url)
event_router = get_event_router(supabase_url)
user_router = get_users_router(supabase_url)

# ルーターの追加
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "うぃっす〜"}

@app.head("/monitor")
def read_root():
    return {"Hello": "うぃっす〜"}

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/events/id")
def add_event_id(event:EventID):
    today_event_id_list.append(event.event_id)
    return {"message": "Event ID added successfully", "today_event_id_list": today_event_id_list}

@app.post("/attendances/{event_id}/{user_id}",response_model=AttendancesResponse)
def send_arrival_time_info(event_id: int, user_id: int):
    with engine.connect() as conn:
        query = text("SELECT * FROM attendances WHERE event_id = :event_id AND user_id = :user_id")
        result = conn.execute(query, {"event_id": event_id, "user_id": user_id}).mappings()
        attendances = [Attendances(**row) for row in result]
        if attendances:
            return AttendancesResponse(message="Attendance data retrieved successfully")
        else:
            return AttendancesResponse(message="No attendance found for this event and user.")
        
@app.websocket("/ws/ranking")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    connected_clients: Dict[int, WebSocket] = {}
    user_locations: Dict[int, Location] = {}
    
    today_event_id_list.append(43)
    event_id = today_event_id_list[0]
    event_deadline_time = websocket_service.calculate_deadline(event_id)
    
    try:
        await websocket.send_text(json.dumps({
            "action": "connected",
            "message": "WebSocket connection established"
        }))

        while True:
            now = datetime.now(timezone.utc)

            if now >= event_deadline_time:
                today_event_id_list.pop(0)
                finish_message = {
                    "action": "tikokulympic_finished",
                    "message": "この遅刻リンピックは終了しました。"
                }
                for client_websocket in connected_clients.values():
                    await client_websocket.send_text(json.dumps(finish_message))
                distances.delete_all_distance()
                for client_websocket in connected_clients.values():
                    await client_websocket.close()

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
                event.add_arrival_time(finish_message, event_id)
                print("success")
                

    except Exception as e:
        print(f"WebSocket error: {e}")
        
@app.get("/check")
def read_root():
    return today_event_id_list

from service.notification import SendNotification
notification=SendNotification(supabase_url)

@app.get("/remind")
def send_notification():
    response = notification.send_remind(event_id=44)
    return response