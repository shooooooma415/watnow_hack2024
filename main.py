from fastapi import FastAPI,WebSocket,Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import schedule
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import os
from sqlalchemy import create_engine, text
from model.event import Location,EventID
from model.websocket import FinishMessage
from repository.event import Event
from repository.distance import Distance
from service.websocket import WebSocketService
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime,timezone
import json

# ルーターの呼び出し
from routers.auth import get_auth_router
from routers.event import get_event_router
from routers.user import get_users_router
from routers.attendance import get_attendances_router

load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')

engine = create_engine(supabase_url)
event = Event(supabase_url)
websocket_service = WebSocketService(supabase_url)
distances = Distance(supabase_url)

today_event_id_list: List[int] = []

from service.notification import SendNotification
notification=SendNotification(supabase_url)

async def tick():
    # notification.send_renew_aliase(57)
    print("hoge")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(tick, "interval", seconds=60)
    scheduler.start()
    
    try:
        yield
    finally:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

# ルーターの取得
auth_router = get_auth_router(supabase_url)
event_router = get_event_router(supabase_url)
user_router = get_users_router(supabase_url)
attendances_router = get_attendances_router(supabase_url)

# ルーターの追加
app.include_router(auth_router)
app.include_router(event_router)
app.include_router(user_router)
app.include_router(attendances_router)

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

