from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

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
    location_point: str
    cost: int
    message: str
    manager_id: str
    options: Optional[Option]

class Events(BaseModel):
    events: List[Event]
    
class EventResponse(BaseModel):
    event_id: int
    message: str
    
