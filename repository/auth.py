from sqlalchemy import create_engine, text

class Auth:
    def __init__(self,supabase_url:str) ->None:
        self.engine = create_engine(supabase_url)
        
    def get_user_id(self,auth_id:int) -> int:
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

        return result["id"]
    