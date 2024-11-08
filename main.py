from fastapi import FastAPI, WebSocket, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from typing import List, Dict
from datetime import datetime, timezone
import json
import os

from dotenv import load_dotenv

from model.event import Location, EventID
from model.websocket import FinishMessage
from repository.event import Event
from repository.distance import Distance
from repository.profile import Profile
from service.websocket import WebSocketService
from service.notification import SendNotification
from service.fetch_profile import ProfileService

from routers.auth import get_auth_router
from routers.event import get_event_router
from routers.user import get_users_router
from routers.attendance import get_attendances_router
from routers.rankings import get_rankings_router

load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')

engine = create_engine(supabase_url)
event = Event(supabase_url)
websocket_service = WebSocketService(supabase_url)
distances = Distance(supabase_url)
profile = Profile(supabase_url)
notification = SendNotification(supabase_url)
profile_service = ProfileService(supabase_url)

today_event_id_list: List[int] = []

async def send_reminders():
    await notification.send_remind_all_events()
    
async def send_cautions():
    await notification.send_caution_all_events()
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(send_reminders, "cron", hour=22, minute=0)
    scheduler.add_job(send_cautions, "cron", hour=23, minute=0)
    scheduler.start()
    
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(get_auth_router(supabase_url))
app.include_router(get_event_router(supabase_url))
app.include_router(get_users_router(supabase_url))
app.include_router(get_attendances_router(supabase_url))
app.include_router(get_rankings_router(supabase_url))

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

@app.websocket("/ws/events/{event_id}/ranking")
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
                    event.add_arrival_time(user_id, now, event_id)
                    aliase_id = profile_service.judge_aliase(user_id)
                    profile.update_aliase_id(user_id,aliase_id)
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
                
                event.add_arrival_time(finish_message.user_id, finish_message.arrival_time, event_id)
                
                aliase_id = profile_service.judge_aliase(finish_message.user_id)
                profile.update_aliase_id(finish_message.user_id,aliase_id)
                notification.send_renew_aliase(finish_message.user_id)
                
                print("success")
                

    except Exception as e:
        print(f"WebSocket error: {e}")
        
@app.get("/check")
def read_root():
    return today_event_id_list

from service.notification import SendNotification
notification=SendNotification(supabase_url)

@app.get("/remind/{event_id}")
def send_notification(event_id:int):
    response = notification.send_remind(event_id)
    return response

