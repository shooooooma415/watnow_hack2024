from model.event import Author,Location,PostEvent,ArrivalTime,ArrivalTimeList,GetEvent,Events,Option,Participants
from model.attendances import Attendances,AttendancesResponse
from sqlalchemy import create_engine, text
from typing import List,Dict,Optional
from datetime import datetime,timedelta,timezone
from model.websocket import FinishMessage

class Event():
    def __init__(self, supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)
    
    def get_author(self, event_id: int) -> Optional[Author]:
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT u.id, u.name 
                FROM events e 
                JOIN users u 
                ON e.author_id = u.id 
                WHERE e.id = :event_id
            """), {"event_id": event_id}).mappings().first()
            
            if result:
                user_data = Author(
                    author_id=result.get("id"),
                    author_name=result.get("name")
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
            
            event_data = GetEvent(
                id = event_id,
                title=result.get('title'),
                description=result.get('description'),
                is_all_day=result.get('is_all_day'), 
                start_date_time=result.get('start_date_time'),
                end_date_time=result.get('end_date_time'),  
                closing_date_time=result.get('closing_date_time'),
                location_name=result.get('location_name'), 
                cost=result.get('cost'),
                message=result.get('message'), 
                latitude=result.get('latitude'), 
                longitude=result.get('longitude')
            )
            
            return event_data
    
    def get_event_id(self) -> List[int]:
        dt_now = datetime.now(timezone.utc)
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                                        SELECT id 
                                        FROM events 
                                        WHERE end_date_time > :current_time
                                        """),{"current_time": dt_now}).mappings()
        event_ids = [row['id'] for row in result]
        
        return event_ids
    
    def get_location(self,event_id:str) -> Optional[Location]:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                                    """
                                    SELECT latitude,longitude 
                                    FROM events 
                                    WHERE id = :event_id
                                    """
                                    ), 
                                    {"event_id": event_id}).mappings().first()
            latitude = result.get("latitude")
            longitude = result.get("longitude")
            location = Location(latitude = latitude,
                                longitude = longitude
                                )
        return location
    
    def get_start_time(self,event_id:str) ->Optional[datetime]:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT start_date_time FROM events WHERE id = :event_id"), 
                                    {"event_id": event_id}).mappings().first()
            start_time = result.get("start_date_time")
        if result is None:
            return None
        
        return start_time
    
    def get_tomorrow_event_id(self) -> List[int]:
        dt_now = datetime.now(timezone.utc)
        dt_2days_later = dt_now + timedelta(days=2)
        lower = dt_now.replace(hour=23, minute=59, second=59)
        upper = dt_2days_later.replace(hour=0, minute=0, second=0)
        print(text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper})
        with self.engine.connect() as conn:
            query = conn.execute(
                text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper}
            )
            result = query.fetchall()
            print(f"クエリ結果: {result}")
            notification_event_id_list = [row[0] for row in result]
        
        return notification_event_id_list
    
    def get_event_title(self,event_id:int) -> Optional[str]:
        with self.engine.connect() as conn:
            query = conn.execute(
                text("SELECT title FROM events WHERE id = :id"),
                {"id": event_id}
            ).mappings()
            
            result = query.fetchone()
            event_title = result['title']
        return event_title
    
    def get_notification_event_id(self) -> List[int]:
        dt_now = datetime.now(timezone.utc)
        dt_2days_later = dt_now + timedelta(days=2)
        lower = dt_now.replace(hour=23, minute=59, second=59)
        upper = dt_2days_later.replace(hour=0, minute=0, second=0)
        with self.engine.connect() as conn:
            query = conn.execute(
                text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper}
            )
            result = query.fetchall()
            notification_event_id_list = [row[0] for row in result]
        
        return notification_event_id_list
    
    def add_events(self, input: PostEvent):
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

        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(text("""
                    INSERT INTO events (
                        title, description, is_all_day, start_date_time, end_date_time, closing_date_time, location_name, cost, message, author_id, latitude, longitude
                    ) 
                    VALUES (
                        :title, :description, :is_all_day, :start_time, :end_time, :closing_time, :location_name, :cost, :message, :author_id, :latitude, :longitude
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
            
        return result_id

    def add_option(self, event_id: str) -> None:
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        """
                        INSERT INTO options (event_id, option)
                        VALUES
                            (:event_id, '参加'),
                            (:event_id, '不参加'),
                            (:event_id, '途中から参加')
                        """
                    ),
                    {"event_id": event_id}
                    )
                
    def delete_event(self,event_id) -> None:
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text("DELETE FROM events WHERE id = :event_id"),{"event_id": event_id})
    
    def add_arrival_time(self,user_id:int,arrival_time:datetime,event_id:int) -> None:
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(
                    text(
                        """
                        INSERT INTO attendances (event_id,user_id,arrival_time) 
                        VALUES (:event_id,:user_id,:arrival_time)
                        """
                    ),
                    {"event_id": event_id, "user_id": user_id, "arrival_time":arrival_time}
                    )
    
    def get_arrival_time_list(self,event_id) -> ArrivalTimeList:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT user_id,arrival_time FROM attendances WHERE event_id = :event_id"),
                {"event_id": event_id}
            ).mappings().fetchall()

        arrival_time_list = [
            ArrivalTime(
                user_id=row['user_id'],
                arrival_time=row['arrival_time']
            ) for row in result
        ]

        return ArrivalTimeList(arrival_time_list=arrival_time_list)
    
    def get_all_delay_time(self,user_id:int) ->List[float]:
        with self.engine.connect() as conn:
            query = conn.execute(
                text(
                    """
                    SELECT a.arrival_time - e.start_date_time
                    FROM attendances a
                    JOIN events e
                    ON a.event_id = e.id
                    WHERE a.user_id = :user_id
                    """),
                {"user_id": user_id,}
            )
            result = query.fetchall()
            delay_time_list = [float(int(row[0].total_seconds() / 60)) for row in result]
            
        return delay_time_list
    
    def add_attendance(self,user_id:int,event_id:int):
        with self.engine.connect() as conn:
            query = text("SELECT * FROM attendances WHERE event_id = :event_id AND user_id = :user_id")
            result = conn.execute(query, {"event_id": event_id, "user_id": user_id}).mappings()
            attendances = [Attendances(**row) for row in result]
            if attendances:
                return AttendancesResponse(message="Attendance data retrieved successfully")
            else:
                return AttendancesResponse(message="No attendance found for this event and user.")