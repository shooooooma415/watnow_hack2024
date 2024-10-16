from fastapi import FastAPI,WebSocket,Request,status,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from model.event import PostEvent,Events,EventResponse,Location
from model.profile import Profile
from model.auth import SignUp,SuccessResponse
from model.attendances import Attendances,AttendancesResponse
from repository.get_event import GetEvent
from repository.add_event import AddEvent
from service.fetch_event import EventService
from service.websocket import WebSocketService
from service.fetch_profile import ProfileService
from service.notification import today_event_id_list
import os
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime
import json

load_dotenv()

app = FastAPI()
supabase_url = os.getenv('SUPABASE_URL')
engine = create_engine(supabase_url)
get_event = GetEvent(supabase_url)
add_event = AddEvent(supabase_url)
event = EventService(supabase_url)
websocket_service = WebSocketService(supabase_url)
profile_service = ProfileService(supabase_url)



@app.get("/")
def read_root():
    return {"Hello": "うぃっす〜"}

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/signup")
def signup(input:SignUp):
    user_name = input.user_name
    auth_id = input.auth_id
    token = input.token
    with engine.connect() as conn:
        with conn.begin():
            result = conn.execute(text(f"INSERT INTO users(name, auth_id, token) VALUES(:name, :auth_id, :token) RETURNING id"),
                {'name': user_name, 'auth_id': auth_id, 'token': token})
            user_id = int(result.scalar())
    return {"id": user_id}
    

@app.get("/events/board",response_model = Events)
def get_events_board():
    events_board = event.fetch_all_events()
    return events_board


@app.post("/events",response_model=EventResponse)
def add_events_board(input: PostEvent):
    event_id = add_event.add_events(input)
    add_event.add_option(event_id)
    response = EventResponse(event_id=event_id, message="Event created successfully")
    return response

@app.post("/events/{event_id}/votes",response_model=SuccessResponse)
def votes(event_id: int):
    pass

@app.get("/users/{user_id}/profile",response_model=Profile)
def get_name(user_id: int):
    profile = profile_service.fetch_profile(user_id)
    
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return profile

@app.put("/users/{user_id}/profile")
def renew_profile():
    pass

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
    event_id = today_event_id_list.pop(0)
    connected_clients: Dict[str, WebSocket] = {}
    user_locations: Dict[str, Location] = {}
    user_distances: Dict[str, float] = {}
    
    event_deadline_time = websocket_service.calculate_deadline_time(event_id)
    
    while True:
        try:
            while True:
                if datetime.now() >= event_deadline_time:
                    finish_message = {
                        "action": "tikokulympic_finished",
                        "message": "この遅刻リンピックは終了しました。"
                    }
                    
                    for client_websocket in connected_clients.values():
                        await client_websocket.send_text(json.dumps(finish_message))
                    
                    for client_websocket in connected_clients.values():
                        await client_websocket.close()
                    break
            
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["action"] == "update_location":
                user_id = message["user_id"]
                latitude = float(message["latitude"])
                longitude = float(message["longitude"])
                
                user_locations[user_id] = Location(latitude=latitude, longitude=longitude)
                
                distance = websocket_service.calculate_distance(event_id,user_locations[user_id])
                user_distances[user_id] = distance
                
                await websocket_service.send_ranking(websocket, user_distances)
                
            elif message["action"] == "get_ranking":
                await websocket_service.send_ranking(websocket,user_distances)
            
            elif message["action"] == "arrival_notification":
                user_id = message["user_id"]
                if user_id in connected_clients:
                    client_websocket = connected_clients[user_id]
                    await client_websocket.close()
                    del connected_clients[user_id]
                
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            await websocket.close()
            break