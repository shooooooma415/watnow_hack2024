from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Participant(BaseModel):
    user_id: int
    user_name: str

class Option(BaseModel):
    title: str
    participant_count: int
    participants: List[Optional[Participant]]

class Event(BaseModel):
    title: str
    description: str
    is_all_day: bool
    start_time: datetime
    end_time: datetime
    closing_time: datetime
    location_name: str
    cost: int
    message: str
    manager_id: int
    latitude: float
    longitude: float
    options: Optional[Option]  

class GetEvent(BaseModel):
    id: int
    title: str
    description: str
    is_all_day: bool
    start_date_time: datetime
    end_date_time: datetime
    closing_date_time: datetime
    location_name: str
    latitude: float
    longitude: float
    cost: float
    message: str
    manager_id: int
    options: Optional[str] = None


class Events(BaseModel):
    events: list[GetEvent]
    
class EventResponse(BaseModel):
    event_id: int
    message: str
    
