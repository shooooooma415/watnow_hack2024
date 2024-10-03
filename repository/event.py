from model.event import PostEvent,EventResponse,User,Participants,Author,GetEvent,Option
from sqlalchemy import create_engine, text, Column, Integer, String, TIMESTAMP, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import List,Dict,Optional

class EventRepo():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)

    def add_events(self, input: PostEvent) -> Optional[EventResponse]:
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
        author_id = input.author_id
        option = input.options.title if input.options else None

        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(text("""
                    INSERT INTO events (
                        title, description, is_all_day, start_date_time, end_date_time, closing_date_time, location_name, cost, message, author_id, latitude, longitude
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
                    'author_id': author_id,
                    'latitude': latitude,
                    'longitude': longitude
                })
                
                result_id = int(result.scalar()) 
                
                if option:
                    conn.execute(text("INSERT INTO options (event_id, option) VALUES (:event_id, :option)"), {
                        "event_id": result_id,
                        "option": option
                    })
        return EventResponse(event_id=result_id, message="Event created successfully")
    
    def convert_to_datetime(self,time_field):
        if isinstance(time_field, datetime):
            return time_field
        return datetime.combine(datetime.today(), time_field) 
    
    def get_option(self, event_id: int) -> Dict[int, str]:
        option_dict = {}
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id, o.option FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                option_dict[row[0]] = row[1]
        return option_dict

    def get_participants(self, option_id: int) -> Optional[Participants]:
        user_list = []
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT u.id, u.name 
                    FROM votes v 
                    JOIN users u 
                    ON v.user_id = u.id 
                    WHERE v.option_id = :id
                    """),
                {"id": option_id}
            ).fetchall()

            for row in result:
                user_data = User(
                    user_id=str(row[0]), 
                    user_name=str(row[1])
                )
                user_list.append(user_data)
        return Participants(participants=user_list) if user_list else None


    def get_author(self, event_id: int) -> Optional[Author]:
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT u.id, u.name 
                FROM events e 
                JOIN users u 
                ON e.author_id = u.id 
                WHERE e.id = :event_id
            """), {"event_id": event_id}).fetchall()
            
            if result:
                for row in result:
                    user_data = Author(
                        user_id=str(row[0]), 
                        user_name=str(row[1])
                    )
                return user_data
            else:
                return None

    def get_event(self, event_id: int) -> Optional[GetEvent]:
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT
                    title, 
                    description, 
                    is_all_day, 
                    start_date_time, 
                    end_date_time, 
                    closing_date_time, 
                    location_name, 
                    cost, 
                    message, 
                    latitude, 
                    longitude
                FROM events
                WHERE id = :event_id
                """), 
            {"event_id": event_id}).mappings().first()
            
            if result is None:
                return None
            
            is_all_day= result.get('is_all_day')
            start_date_time = result.get('start_date_time')
            end_date_time = result.get('end_date_time')
            closing_date_time = result.get('closing_date_time')
            
            event_data = GetEvent(
                title=result.get('title'),
                description=result.get('description'),
                is_all_day=is_all_day, 
                start_date_time=start_date_time,
                end_date_time=end_date_time,  
                closing_date_time=closing_date_time,
                location_name=result.get('location_name'), 
                cost=result.get('cost'),
                message=result.get('message'), 
                latitude=result.get('latitude'), 
                longitude=result.get('longitude')
            )
            
            return event_data
    
    def get_event_id(self) -> List[int]:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM events")).mappings().fetchall()
        event_ids = [row['id'] for row in result]
        
        return event_ids

