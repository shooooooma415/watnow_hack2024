from fastapi import APIRouter
from model.event import PostEvent,Events,EventResponse,EventID,ArrivalTimeRanking
from model.auth import SuccessResponse
from model.attendances import RequestVote
from repository.event import Event
from service.fetch_event import EventService
from service.vote import Vote
from repository.get_attendance import GetAttendance
from repository.add_votes import AddVotes

def get_auth_router(supabase_url: str):
    router = APIRouter(prefix="/events", tags=["Event"])
    event = Event(supabase_url)
    event_service = EventService(supabase_url)
    vote = Vote(supabase_url)
    get_attendance = GetAttendance(supabase_url)
    add_votes = AddVotes(supabase_url)

    @router.get("/events/board",response_model = Events)
    def get_events_board():
        events_board = event_service.fetch_all_events()
        return events_board

    @router.post("/events",response_model=EventResponse)
    def insert_event(input: PostEvent):
        event_id = event.add_events(input)
        event.add_option(event_id)
        response = EventResponse(event_id=event_id, message="Event created successfully")
        return response

    @router.delete("/events/{event_id}",response_model=SuccessResponse)
    def delete_event(event_id:int):
        event.delete_event(event_id)
        return SuccessResponse(is_success = True)

    @router.post("/events/{event_id}/votes",response_model=SuccessResponse)
    def votes(input:RequestVote, event_id:int):
        vote.delete_vote(event_id,input.user_id)
        option_id = get_attendance.get_option_id(event_id,input.option)
        add_votes.insert_vote(option_id,input.user_id)
        
        return SuccessResponse(is_success = True)

    @router.get("/events/{event_id}/arrival_ranking",response_model=List[ArrivalTimeRanking])
    def get_arrival_ranking(event_id:int):
        ranking = event_service.fetch_arrival_time_ranking(event_id)
        return ranking

    @router.post("/events/id")
    def add_event_id(event:EventID):
        today_event_id_list.append(event.event_id)
        return {"message": "Event ID added successfully", "today_event_id_list": today_event_id_list}