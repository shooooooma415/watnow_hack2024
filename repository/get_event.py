from model.event import User,Participants,Author,FetchEvent,Location
from sqlalchemy import create_engine, text
from typing import List,Dict,Optional

class GetEvent():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)
    
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

    def get_event(self, event_id: int) -> Optional[FetchEvent]:
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
            
            event_data = FetchEvent(
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
            result = conn.execute(text("SELECT id FROM events")).mappings()
        event_ids = [row['id'] for row in result]
        
        return event_ids
    
    def get_location(self,event_id:str) -> Optional[Location]:
        with self.engine.connect() as conn:
            result = conn.execute(text("""SELECT latitude,longitude 
                                        FROM events 
                                        WHERE id = :event_id"""), 
                                    {"event_id": event_id}).mappings().first()
            latitude = result.get("latitude")
            longitude = result.get("longitude")
            location = Location(latitude = latitude,
                                longitude = longitude
                                )
        
        return location
