from pydantic import BaseModel
from datetime import timedelta

class Profile(BaseModel):
    name: str
    alias: str = None
    late_count: int = None
    total_late_time: int = None
    late_percentage: float = None
    on_time_count: int = None

class Delay(BaseModel):
    total_late_time: int = None
    late_count: int = None
    on_time_count: int = None
    late_percentage: float = None