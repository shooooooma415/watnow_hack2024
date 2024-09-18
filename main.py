from fastapi import FastAPI
from sqlalchemy import create_engine, text
from model.event import Events,Event,EventResponse
from model.profile import Profile
from model.auth import Login,SucessResponse,SignUp
from repository.event import EventRepo
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

app = FastAPI()
supabase_url = os.getenv('SUPABASE_URL')
engine = create_engine(supabase_url)
event_repo = EventRepo(supabase_url)



@app.get("/")
def read_root():
    return {"Hello": "World"}


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


@app.post("/events",response_model=EventResponse)
def add_event(input:Event):
    event_id = event_repo.add_events(input)
    return EventResponse(event_id=event_id, message="Event created successfully")

@app.get("/users/{user_id}/profile",response_model=Profile)
def get_profile(user_id: int):
    with engine.connect() as conn:
        query = text("SELECT * FROM users WHERE id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).mappings()
        profiles = [Profile(**row) for row in result]
    return profiles

# @app.put("/users/{user_id}/profile")

# @app.post("/attendances/{event_id}/{user_id}")
