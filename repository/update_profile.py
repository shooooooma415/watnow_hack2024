from sqlalchemy import create_engine, text

class UpdateProfile():
    def __init__(self,supabase_url) -> None:
        self.engine = create_engine(supabase_url)
    
    def update_name(self,user_id, name):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                "UPDATE users SET name = :name WHERE id = :user_id"),
                {"name": name, "user_id": user_id}
                )