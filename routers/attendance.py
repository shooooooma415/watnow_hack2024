from fastapi import APIRouter
from model.attendances import AttendancesResponse
from service.fetch_event import EventService


router = APIRouter(prefix="/attendances", tags=["Attendances"])

def get_attendances_router(supabase_url:str):
    router = APIRouter(prefix="/attendances", tags=["Attendances"])
    fetch_event = EventService(supabase_url)

    @router.post("/{event_id}/{user_id}",response_model=AttendancesResponse)
    def send_arrival_time_info(event_id: int, user_id: int):
        return fetch_event.event.add_attendance(user_id,event_id)
    
    return router