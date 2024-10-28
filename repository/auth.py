from sqlalchemy import create_engine, text
from model.auth import AuthResponse,SignIn,SignUp

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
    
    def create_user_id(self,input:SignUp):
        user_name = input.user_name
        auth_id = input.auth_id
        token = input.token
        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(text(f"INSERT INTO users(name, auth_id, token) VALUES(:name, :auth_id, :token) RETURNING id"),
                    {'name': user_name, 'auth_id': auth_id, 'token': token})
                user_id = int(result.scalar())
        return AuthResponse(id = user_id)