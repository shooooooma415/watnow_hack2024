from sqlalchemy import create_engine, text

class Distance():
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
    
    def is_distance_present(self, user_id: int) -> bool:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT distance FROM locations WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            if result is None or result[0] is None:
                return False
            
            return True
    
    def get_all_distance(self) -> dict:
        distance_dict = dict()
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT user_id, distance FROM locations")
            ).fetchall()

            for row in result:
                distance_dict[row[0]] = row[1]
                
        return distance_dict
    
    def delete_all_distance(self) -> None:
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "DELETE FROM locations"
                ))