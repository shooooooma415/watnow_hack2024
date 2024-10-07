from model.event import PostEvent,EventResponse,User,Participants,Author,FetchEvent,Option
from sqlalchemy import create_engine, text, Column, Integer, String, TIMESTAMP, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import List,Dict,Optional

class PutEvent():
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
        
    return EventResponse(event_id=result_id, message="Event created successfully")

  def convert_to_datetime(self, time_field):
    if isinstance(time_field, datetime):
      return time_field
    return datetime.combine(datetime.today(), time_field)
