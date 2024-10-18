from sqlalchemy import create_engine, text

class GetDistance():
    def __init__(self,supabase_url:str) ->None:
        self.engine = create_engine(supabase_url)
    
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
