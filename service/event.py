from repository.event import EventRepo
from model.event import GetEvent
from sqlalchemy import create_engine, text

class EventService():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)
        self.event_repo = EventRepo(supabase_url)
        
    
    def fetch_event(self, event_id: int) -> GetEvent:
        present = self.event_repo.get_participants(event_id)
        author = self.event_repo.get_author(event_id)
        table_event = self.event_repo.get_event(event_id)     

        title = table_event.title
        description = table_event.description
        is_all_day = table_event.is_all_day
        start_time = table_event.start_date_time
        end_time = table_event.end_date_time
        closing_time = table_event.closing_date_time
        location_name = table_event.location_name
        cost = table_event.cost
        message = table_event.message
        latitude = table_event.latitude
        longitude = table_event.longitude

        event = GetEvent(
            id=event_id,
            title=title,
            description=description,
            author=author,
            is_all_day=is_all_day,
            start_date_time=start_time,
            end_date_time=end_time,
            closing_date_time=closing_time,
            location_name=location_name,
            cost=cost,
            message=message,
            latitude=latitude,
            longitude=longitude,
            options=present
        )

        return event
