from sqlalchemy import create_engine, text

class GetDistance():
    def __init__(self,supabase_url:str) ->None:
        self.engine = create_engine(supabase_url)
    
    def get_all_distance(self) -> dict:
        distance_dict = dict()
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT user_id, distance FROM locations")
            ).fetchall()

            for row in result:
                distance_dict[row[0]] = row[1]
                
        return distance_dict
