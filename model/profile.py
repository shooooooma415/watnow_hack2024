from pydantic import BaseModel

class Profile(BaseModel):
    name: str
    alias: str
    late_count: int
    total_late_time: int
    late_percentage: float
    on_time_count: int