from fastapi import APIRouter
from sqlalchemy import create_engine, text 
from repository.event import Event
from model.attendances import AttendancesResponse

router = APIRouter(prefix="/attendances", tags=["Attendances"])

def get_attendances_router(supabase_url:str):
    router = APIRouter(prefix="/attendances", tags=["Attendances"])
    event = Event(supabase_url)

    @router.post("/{event_id}/{user_id}",response_model=AttendancesResponse)
    def send_arrival_time_info(event_id: int, user_id: int):
        return event.add_attendance(user_id,event_id)
    
    return router