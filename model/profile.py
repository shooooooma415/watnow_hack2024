from pydantic import BaseModel
from datetime import timedelta
from typing import List, Optional

class UserProfile(BaseModel):
    name: str
    alias: Optional[str] = None
    late_count: int = None
    total_late_time: int = None
    late_percentage: float = None
    on_time_count: int = None

class Delay(BaseModel):
    total_late_time: int = None
    late_count: int = None
    on_time_count: int = None
    late_percentage: float = None
    
class Name(BaseModel):
    name: str