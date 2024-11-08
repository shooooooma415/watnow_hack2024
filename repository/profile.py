from sqlalchemy import create_engine, text
from typing import Optional,List,Dict
from datetime import datetime
from model.aliase import AliaseID

class Profile():
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
            ).mappings().fetchall()

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
    
    def get_token(self, user_id:int) -> Optional[str]:
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""SELECT token FROM users WHERE id = :user_id"""),
                {"user_id": user_id}
            ).fetchone()
            
        return result[0] if result else None
    
    def get_remind_tokens(self, option_id:int) -> List[str]:
        token_list = []
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""SELECT u.token FROM votes v JOIN users u ON v.user_id = u.id WHERE v.option_id = :id"""),
                {"id": option_id}
            ).fetchall()
            
            for row in result:
                token_list.append(row[0])
        return token_list
    
    def get_remind_tokens_for_aliased_users(self, option_id:int) -> Dict[int,str]:
        token_dict = dict()
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT u.id, u.token 
                    FROM votes v
                    JOIN users u ON v.user_id = u.id
                    JOIN user_alias ua ON ua.user_id = u.id
                    WHERE v.option_id = :option_id
                    AND ua.aliase_id <= :aliase_id
                    """
                    ),{"option_id": option_id, "aliase_id":AliaseID.ビギナー遅刻者.value}
            ).fetchall()
            if not result:
                return {}
            
            for row in result:
                token_dict[row[0]] = row[1]
                
        return token_dict
    
    def update_name(self,user_id, name):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                "UPDATE users SET name = :name WHERE id = :user_id"),
                {"name": name, "user_id": user_id}
                )
                
    def get_all_delay_time(self,user_id:int) ->List[datetime]:
        with self.engine.connect() as conn:
            query = conn.execute(
                text(
                    """
                    SELECT a.arrival_time - e.start_date_time
                    FROM attendances a
                    JOIN events e
                    ON a.event_id = e.id
                    WHERE a.user_id = :user_id
                    """),
                {"user_id": user_id,}
            )
            result = query.fetchall()
            delay_time_list = [row[0] for row in result]
            
        return delay_time_list
    
    def update_aliase_id(self, user_id:int, aliase_id:int):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                    "UPDATE user_alias SET aliase_id = :aliase_id WHERE user_id = :user_id"),
                    {"aliase_id":aliase_id,"user_id": user_id}
                )
        # return "success" #ここは要件にちょって変える
        
    def get_all_user_id(self) ->List[int]:
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT id from users")).fetchall()
            user_ids = [row[0] for row in result]
        return user_ids
