from pydantic import BaseModel

class SignInResponse(BaseModel):
    user_id : int

class SuccessResponse(BaseModel):
    is_success : bool

class SignUp(BaseModel):
    user_name: str
    auth_id: int
    token: str

class SignIn(BaseModel):
    auth_id:int