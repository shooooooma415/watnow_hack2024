from pydantic import BaseModel

class AuthResponse(BaseModel):
    id : int

class SuccessResponse(BaseModel):
    is_success : bool

class SignUp(BaseModel):
    user_name: str
    auth_id: str
    token: str

class SignIn(BaseModel):
    auth_id:str