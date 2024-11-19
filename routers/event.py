from fastapi import APIRouter
from model.event import PostEvent,Events,EventResponse,ArrivalTimeRanking,FinishedEvents
from model.auth import SuccessResponse
from model.attendances import RequestVote
from service.fetch_event import EventService
from service.vote import Vote
from repository.add_votes import AddVotes
from typing import List

def get_event_router(supabase_url: str):
    router = APIRouter(prefix="/events", tags=["Event"])
    event_service = EventService(supabase_url)
    vote = Vote(supabase_url)
    add_votes = AddVotes(supabase_url)

    @router.get("/board",response_model = Events)
    def get_events_board():
        events_board = event_service.fetch_all_events()
        return events_board
    
    @router.get("/board/finished",response_model = FinishedEvents)
    def get_finished_events_board():
        events_board = event_service.fetch_finished_events()
        return events_board

    @router.post("",response_model=EventResponse)
    def insert_event(input: PostEvent):
        event_id = event_service.event.add_events(input)
        event_service.event.add_option(event_id)
        response = EventResponse(event_id=event_id, message="Event created successfully")
        return response

    @router.delete("/{event_id}",response_model=SuccessResponse)
    def delete_event(event_id:int):
        event_service.event.delete_event(event_id)
        return SuccessResponse(is_success = True)

    @router.post("/{event_id}/votes",response_model=SuccessResponse)
    def votes(input:RequestVote, event_id:int):
        vote.delete_vote(event_id,input.user_id)
        option_id = event_service.get_attendance.get_option_id(event_id,input.option)
        add_votes.insert_vote(option_id,input.user_id)
        
        return SuccessResponse(is_success = True)

    @router.get("/{event_id}/arrival_ranking",response_model=List[ArrivalTimeRanking])
    def get_arrival_ranking(event_id:int):
        ranking = event_service.fetch_arrival_time_ranking(event_id)
        return ranking
    
    return router