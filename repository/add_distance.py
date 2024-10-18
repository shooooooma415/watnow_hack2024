from sqlalchemy import create_engine, text

class AddDistance():
    def __init__(self, supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)

    def is_distance_present(self, user_id: int) -> bool:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT distance FROM locations WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            if result is None:
                return False 
            if result['distance'] is None:
                return False
            
            return True
    
    def insert_distance(self, distance:float, user_id:int):
        with self.engine.connect() as conn:
            conn.execute(text(
                "INSERT INTO locations (distance, user_id) VALUES (:distance, :user_id)"),
                {"distance": distance, "user_id": user_id}
            )
    
    def update_distance(self, distance:float, user_id:int):
        with self.engine.connect() as conn:
            conn.execute(text(
                "UPDATE locations SET distance = :distance WHERE user_id = :user_id"),
                {"distance": distance, "user_id": user_id}
            )