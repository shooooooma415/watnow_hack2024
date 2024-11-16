from fastapi import FastAPI,Request,status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

from application.notification import SendNotification

from routers.auth import get_auth_router
from routers.event import get_event_router
from routers.user import get_users_router
from routers.attendance import get_attendances_router
from routers.rankings import get_rankings_router
from routers.websocket import get_websocket_router

load_dotenv()
supabase_url = os.getenv('SUPABASE_URL')
engine = create_engine(supabase_url)
notification = SendNotification(supabase_url)

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
app.include_router(get_websocket_router(supabase_url))

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

@app.get("/remind/{event_id}")
def send_notification(event_id:int):
    response = notification.send_remind(event_id)
    return response


from service.fetch_profile import ProfileService

profile_service = ProfileService(supabase_url)

@app.get("/check/{user_id}")
def send_notification(user_id:int):
    response = notification.send_next_aliase(user_id)
    return response
