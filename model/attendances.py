from pydantic import BaseModel
from datetime import datetime

class Attendances(BaseModel):
    is_arrival:bool
    arrial_time:datetime

class AttendancesResponse(BaseModel):
    message:str