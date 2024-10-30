from sqlalchemy import create_engine, text
from model.auth import AuthResponse,SignIn,SignUp
from typing import Optional

class Auth:
    def __init__(self,supabase_url:str) ->None:
        self.engine = create_engine(supabase_url)
        
    def get_user_id(self,input:SignIn) -> AuthResponse:
        auth_id = input.auth_id
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id
                    FROM users
                    WHERE auth_id = :auth_id
                    """), {"auth_id": auth_id}
            ).mappings().fetchone()
        
        if result is None:
            return None
        return AuthResponse(id = result["id"])
    
    def create_user(self, input: SignUp) -> Optional[AuthResponse]:
        user_name = input.user_name
        auth_id = input.auth_id
        token = input.token
        aliase_id = 6

        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(
                    text("INSERT INTO users(name, auth_id, token) VALUES(:name, :auth_id, :token) RETURNING id"),
                    {'name': user_name, 'auth_id': auth_id, 'token': token}
                )
                user_id = int(result.scalar())
                conn.execute(
                    text("INSERT INTO user_alias(user_id, aliase) VALUES(:user_id, :aliase_id)"),
                    {'user_id': user_id, 'aliase_id': aliase_id}
                )

        return AuthResponse(id=user_id)
