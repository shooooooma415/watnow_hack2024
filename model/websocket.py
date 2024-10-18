from pydantic import BaseModel

class FinishMessage(BaseModel):
    action: str
    message: str