from fastapi import FastAPI
from sqlalchemy import create_engine, text
from model.event import PostEvent,EventResponse,Events
from model.profile import Profile
from model.auth import Login,SucessResponse,SignUp
from model.attendances import Attendances,AttendancesResponse
from repository.event import EventRepo
from service.event import EventService
import os
from dotenv import load_dotenv
from typing import List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status
from repository.push_service import PushService

load_dotenv()

app = FastAPI()
supabase_url = os.getenv('SUPABASE_URL')
engine = create_engine(supabase_url)
event_repo = EventRepo(supabase_url)
push_service = PushService(supabase_url)
event = EventService(supabase_url)


@app.get("/")
def read_root():
    return {"Hello": "World"}

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


@app.post("/events", response_model=EventResponse)
def add_event(input: PostEvent):
    event_response = event_repo.add_events(input)
    return event_response

@app.get("/users/{user_id}/profile",response_model=Profile)
def get_profile(user_id: int):
    with engine.connect() as conn:
        query = text("SELECT * FROM users WHERE id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).mappings()
        name = result['name']
        
    return Profile()

@app.get("/users/{user_id}/name")
def get_name(user_id: int):
    with engine.connect() as conn:
        query = text("SELECT name FROM users WHERE id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).mappings().first()

        if result:
            name = result['name']
            return {"name": name}
        else:
            return {"error": "User not found"}       

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
        

@app.get("/send")
def send_message():
    event_id_list = push_service.get_event_id()
    response_list = []
    for event_id in event_id_list:
        response = push_service.send_notification(event_id)
        response_list.append(response)
    return response_list

# send_message()