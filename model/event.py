from pydantic import BaseModel
from datetime import datetime,timedelta
from typing import List, Optional
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(BaseModel):
    user_id: int = None
    user_name: str = None

class Author(BaseModel):
    author_id: int = None
    author_name: str = None

class Participants(BaseModel):
    participants: Optional[List[User]] = None

class Option(BaseModel):
    title: str = None
    participant_count: int = None
    participants: Optional[Participants] = None

class PostEvent(BaseModel):
    title: str
    description: str
    is_all_day: bool
    start_time: datetime
    end_time: datetime
    closing_time: datetime
    location_name: str
    cost: float
    message: str
    author_id: int
    latitude: float
    longitude: float

class GetEvent(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    is_all_day: Optional[bool] = None
    start_date_time: Optional[datetime] = None
    end_date_time: Optional[datetime] = None
    closing_date_time: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cost: Optional[float] = None
    message: Optional[str] = None

class FetchEvent(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    author: Optional[Author] = None
    description: Optional[str] = None
    is_all_day: Optional[bool] = None
    start_date_time: Optional[datetime] = None
    end_date_time: Optional[datetime] = None
    closing_date_time: Optional[datetime] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    cost: Optional[float] = None
    message: Optional[str] = None
    options: Optional[List[Option]] = None


class Events(BaseModel):
    events: Optional[List[FetchEvent]] = None
    
class EventResponse(BaseModel):
    event_id: int
    message: str
    
class Location(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]
    
class EventID(BaseModel):
    event_id: int

class ArrivalTime(BaseModel):
    user_id: int
    arrival_time: Optional[datetime]

class ArrivalTimeList(BaseModel):
    arrival_time_list: Optional[List[ArrivalTime]]
    
class ArrivalTimeRanking(BaseModel):
    id: int
    position:int
    name: str
    alias: Optional[str] = None
    arrival_time: int