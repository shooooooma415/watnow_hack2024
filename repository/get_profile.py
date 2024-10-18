from sqlalchemy import create_engine, text
from typing import Optional,List

class GetProfile():
    def __init__(self,supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)
    
    def get_delay_time(self, user_id: str) -> Optional[List]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT a.arrival_time - e.start_date_time AS delay_time  -- カラム名を修正
                    FROM events e
                    JOIN attendances a
                    ON e.id = a.event_id
                    WHERE a.user_id = :user_id
                    """), {"user_id": user_id}
            ).fetchall()

        delay_times = [row['delay_time'] for row in result if row['delay_time'] is not None]
        return delay_times if delay_times else None

    
    def get_aliase_id(self, user_id: str) -> Optional[int]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT ua.aliase_id
                    FROM users u
                    JOIN user_alias ua 
                    ON u.id = ua.user_id
                    WHERE u.id = :user_id
                    """), {"user_id": user_id}
            ).mappings().fetchone() 

        if result is None:
            return None

        return result["aliase_id"]

    def get_aliase(self, user_id: str) -> Optional[str]:
        aliase_id = self.get_aliase_id(user_id)
        
        if aliase_id is None:
            return None

        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT aliase
                    FROM aliases
                    WHERE id = :aliase_id
                    """), {"aliase_id": aliase_id} 
            ).mappings().fetchone()

        if result is None:
            return None

        return result["aliase"]

    def get_name(self, user_id: int) -> Optional[str]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT name
                    FROM users
                    WHERE id = :id
                    """), {"id": user_id}
            ).mappings().fetchone()
        
        if result is None:
            return None

        return result["name"]
    
    def get_token(self, option_id_list: List[int]) -> List[str]:
        token_list = []
        for option_id in option_id_list:
            print(f"オプションID: {option_id} に対してトークン取得中")
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("""SELECT u.token FROM votes v JOIN users u ON v.user_id = u.id WHERE v.option_id = :id"""),
                    {"id": option_id}
                ).fetchall()
                
                for row in result:
                    token_list.append(row[0])
        return token_list
