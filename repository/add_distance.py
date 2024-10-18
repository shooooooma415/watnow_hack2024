from sqlalchemy import create_engine, text

class AddDistance():
    def __init__(self, supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)
    
    def insert_distance(self, distance:float, user_id:int):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "INSERT INTO locations (distance, user_id) VALUES (:distance, :user_id)"),
                    {"distance": distance, "user_id": user_id}
                )
    
    def update_distance(self, distance:float, user_id:int):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "UPDATE locations SET distance = :distance WHERE user_id = :user_id"),
                    {"distance": distance, "user_id": user_id}
                )