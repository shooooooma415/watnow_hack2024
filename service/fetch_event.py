from repository.event import Event
from repository.get_attendance import GetAttendance
from repository.profile import Profile
from model.event import Participants,FinishedEvents
from typing import List
from model.event import FetchEvent, Events,Option,ArrivalTimeList,ArrivalTimeRanking
from sqlalchemy import create_engine

class EventService():
    def __init__(self, supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)
        self.event = Event(supabase_url)
        self.get_attendance = GetAttendance(supabase_url)
        self.profile = Profile(supabase_url)

    def fetch_option(self, event_id: int) -> List[Option]:
        response = []
        option_dict = self.get_attendance.get_option(event_id)
        for option_id, title in option_dict.items():
            participants = self.get_attendance.get_participants(option_id)
            if participants:
                participant_list = Participants(participants=participants.participants)
            else:
                participant_list = None
            
            participant_count = len(participants.participants) if participants else 0
            
            option = Option(
                title=title,
                participant_count=participant_count,
                participants=participant_list
            )
            response.append(option)
        return response


    def fetch_event(self, event_id: int) -> FetchEvent:
        options = self.fetch_option(event_id)

        author = self.event.get_author(event_id)
        table_event = self.event.get_event(event_id)

        event = FetchEvent(
            id=event_id,
            title=table_event.title,
            description=table_event.description,
            author=author,
            is_all_day=table_event.is_all_day,
            start_date_time=table_event.start_date_time,
            end_date_time=table_event.end_date_time,
            closing_date_time=table_event.closing_date_time,
            location_name=table_event.location_name,
            cost=table_event.cost,
            message=table_event.message,
            latitude=table_event.latitude,
            longitude=table_event.longitude,
            options=options if options else None 
        )
        return event


    def fetch_all_events(self) -> Events:
        event_ids = self.event.get_event_id()
        event_list = []
        for event_id in event_ids:
            event = self.fetch_event(event_id)
            event_list.append(event)
        return Events(events=event_list)
    
    
    def fetch_arrival_time_ranking(self, event_id: int) -> List[ArrivalTimeRanking]:
        start_time = self.event.get_start_time(event_id)
        if not start_time:
            raise ValueError(f"Start time not found for event ID {event_id}")
        
        arrival_time_list_obj = self.event.get_arrival_time_list(event_id)
        if not arrival_time_list_obj.arrival_time_list:
            return []

        ranking_list = []
        
        for idx, arrival_time_obj in enumerate(arrival_time_list_obj.arrival_time_list):
            user_id = arrival_time_obj.user_id
            arrival_time = arrival_time_obj.arrival_time

            name = self.profile.get_name(user_id)
            alias = self.profile.get_aliase(user_id) or "No alias"

            time_difference = int((arrival_time - start_time).total_seconds() / 60)

            ranking = ArrivalTimeRanking(
                id=user_id,
                position=idx + 1,
                name=name,
                alias=alias,
                arrival_time=time_difference  
            )
            ranking_list.append(ranking)

        return ranking_list


    
    def fetch_finished_events(self) -> FinishedEvents:
        event_ids = self.event.get_finished_event_id()
        event_list = []
        for event_id in event_ids:
            event = self.event.get_finished_event(event_id)
            event_list.append(event)
        return FinishedEvents(events=event_list)
