from fastapi import FastAPI
from sqlalchemy import create_engine, text
from model.event import Events,Event,EventResponse
from model.profile import Profile
from model.auth import Login,SucessResponse,SignUp
from model.attendances import Attendances,AttendancesResponse
from repository.event import EventRepo
import os
from dotenv import load_dotenv
from typing import List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request, status
import firebase_admin
from firebase_admin import credentials

load_dotenv()

app = FastAPI()
supabase_url = os.getenv('SUPABASE_URL')
engine = create_engine(supabase_url)
event_repo = EventRepo(supabase_url)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/signup", response_model=SucessResponse)
def signup(input:SignUp):
    user_name = input.user_name
    auth_id = input.auth_id
    token = input.token
    with engine.connect() as conn:
        result = conn.execute(text("INSERT INTO users(name, auth_id, token) VALUES(:user_name, :auth_id, :token)"),
            {"user_name": user_name, "auth_id": auth_id, "token": token}).mappings()
        
    return SucessResponse(success=True)
    

@app.get("/events/board",response_model=Events)
def get_events_board():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM events")).mappings()
        event_list = [Event(**row) for row in result]
    return Events(events=event_list)


@app.post("/events", response_model=EventResponse)
def add_event(input: Event):
    event_response = event_repo.add_events(input)
    return event_response

@app.get("/users/{user_id}/profile",response_model=Profile)
def get_profile(user_id: int):
    with engine.connect() as conn:
        query = text("SELECT * FROM users WHERE id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).mappings()
        profiles = [Profile(**row) for row in result]
    return profiles

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