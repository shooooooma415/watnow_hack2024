from fastapi import FastAPI,WebSocket,Request,status,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from model.event import PostEvent,Events,EventResponse,Location,EventID
from model.profile import Profile,Name
from model.auth import SignUp,SuccessResponse
from model.attendances import Attendances,AttendancesResponse,RequestVote
from repository.get_event import GetEvent
from repository.add_event import AddEvent
from repository.add_distance import AddDistance
from repository.get_distance import GetDistance
from repository.add_votes import AddVotes
from repository.get_attendance import GetAttendance
from repository.update_profile import UpdateProfile
from service.fetch_event import EventService
from service.websocket import WebSocketService
from service.fetch_profile import ProfileService
from service.vote import Vote
import os
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime,timezone
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
add_distance = AddDistance(supabase_url)
get_distance = GetDistance(supabase_url)
vote = Vote(supabase_url)
add_votes = AddVotes(supabase_url)
get_attendance = GetAttendance(supabase_url)
update_profile = UpdateProfile(supabase_url)

today_event_id_list: List[int] = []

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
def insert_event(input: PostEvent):
    event_id = add_event.add_events(input)
    add_event.add_option(event_id)
    response = EventResponse(event_id=event_id, message="Event created successfully")
    return response

@app.delete("/events/{event_id}/delete")
def delete_event(event_id:int):
    pass

@app.post("/events/{event_id}/votes",response_model=SuccessResponse)
def votes(input:RequestVote, event_id:int):
    vote.delete_vote(event_id,input.user_id)
    option_id = get_attendance.get_option_id(event_id,input.option)
    add_votes.insert_vote(option_id,input.user_id)
    
    return SuccessResponse(is_success = True)

@app.get("/users/{user_id}/profile",response_model=Profile)
def get_name(user_id: int):
    profile = profile_service.fetch_profile(user_id)
    
    if profile is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return profile

@app.put("/users/{user_id}/profile/name", response_model=SuccessResponse)
def renew_profile(input:Name,user_id:int):
    update_profile.update_name(user_id,input.name)
    return SuccessResponse(is_success = True)

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
        
@app.post("/events/id")
def add_event_id(event:EventID):
    today_event_id_list.append(event.event_id)
    return {"message": "Event ID added successfully", "today_event_id_list": today_event_id_list}
        
@app.websocket("/ws/ranking")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    connected_clients: Dict[int, WebSocket] = {}
    user_locations: Dict[int, Location] = {}
    
    today_event_id_list.append(37)
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
                get_distance.delete_all_distance()
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
                
                if get_distance.is_distance_present(user_id) == True:
                    add_distance.update_distance(distance,user_id)

                else:
                    add_distance.insert_distance(distance,user_id)
                    
                await websocket_service.send_ranking(websocket)

            elif message["action"] == "get_ranking":
                await websocket_service.send_ranking(websocket)

            elif message["action"] == "arrival_notification":
                user_id = message['user_id']
                if user_id in connected_clients:
                    client_websocket = connected_clients[user_id]
                    del connected_clients[user_id]
                    await client_websocket.close()

    except Exception as e:
        print(f"WebSocket error: {e}")
        
@app.get("/check")
def read_root():
    return today_event_id_list