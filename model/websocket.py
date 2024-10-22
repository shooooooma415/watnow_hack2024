from pydantic import BaseModel
from datetime import datetime

class FinishMessage(BaseModel):
    action: str
    user_id: int
    arrival_time: datetime