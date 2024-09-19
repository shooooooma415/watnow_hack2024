from model.event import Event, EventResponse
from sqlalchemy import create_engine, text, Column, Integer, String, TIMESTAMP, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

class EventRepo():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)

    def add_events(self, input: Event) -> EventResponse:
        title = input.title
        description = input.description
        is_all_day = input.is_all_day
        start_time = input.start_time
        end_time = input.end_time
        closing_time = input.closing_time
        location_name = input.location_name
        latitude = input.latitude
        longitude = input.longitude
        cost = input.cost
        message = input.message
        manager_id = input.manager_id
        option = input.options.title if input.options else None

        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(text("""
                    INSERT INTO events (
                        title, description, is_all_day, start_date_time, end_date_time, closing_date_time, location_name, cost, message, manager_id, latitude, longitude
                    ) 
                    VALUES (
                        :title, :description, :is_all_day, :start_time, :end_time, :closing_time, :location_name, :cost, :message, :manager_id, :latitude, :longitude
                    ) RETURNING id 
                """), {
                    'title': title,
                    'description': description,
                    'is_all_day': is_all_day,
                    'start_time': start_time,
                    'end_time': end_time,
                    'closing_time': closing_time,
                    'location_name': location_name,
                    'cost': cost,
                    'message': message,
                    'manager_id': manager_id,
                    'latitude': latitude,
                    'longitude': longitude
                })
                
                result_id = int(result.scalar()) 
                
                if option:
                    conn.execute(text("INSERT INTO options (event_id, title) VALUES (:event_id, :option)"), {
                        "event_id": result_id,
                        "option": option
                    })
        return EventResponse(event_id=result_id, message="Event created successfully")
    
    
    def convert_to_datetime(self,time_field):
        if isinstance(time_field, datetime):
            return time_field
        return datetime.combine(datetime.today(), time_field) 