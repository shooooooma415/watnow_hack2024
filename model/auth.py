from pydantic import BaseModel

class Login(BaseModel):
    user_name : str
    user_id : int

class SuccessResponse(BaseModel):
    is_success : bool

class SignUp(BaseModel):
    user_name: str
    auth_id: int
    token: str