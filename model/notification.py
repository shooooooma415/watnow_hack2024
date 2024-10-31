from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Notification(BaseModel):
    title:str
    body:str
    
class RemindData(BaseModel):
    content:str
    event_id:str
    title:str
    location:str
    latitude:str
    longitude:str
    start_time:str
    
class AliaseData(BaseModel):
    content: str
    aliase: str
