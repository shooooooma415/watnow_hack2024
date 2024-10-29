from fastapi import APIRouter
from model.auth import SignUp, SignIn, AuthResponse
from repository.auth import Auth

def get_auth_router(supabase_url: str):
    router = APIRouter(prefix="/auth", tags=["Authentication"])
    auth = Auth(supabase_url)

    @router.post("/signup", response_model=AuthResponse)
    def signup(input: SignUp):
        return auth.create_user_id(input)

    @router.post("/signin", response_model=AuthResponse)
    def signin(input: SignIn):
        return auth.get_user_id(input)

    return router
