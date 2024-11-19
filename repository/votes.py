from model.event import User,Participants
from sqlalchemy import create_engine, text
from typing import List,Dict,Optional

class Votes():
    def __init__(self,supabase_url:str) -> None:
        self.engine = create_engine(supabase_url)
        
    def get_option(self, event_id: int) -> Dict[int, str]:
        option_dict = {}
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id, o.option FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                option_dict[row[0]] = row[1]
        return option_dict

    def get_participants(self, option_id: int) -> Optional[Participants]:
        user_list = []
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT u.id, u.name 
                    FROM votes v 
                    JOIN users u 
                    ON v.user_id = u.id 
                    WHERE v.option_id = :id
                    """),
                {"id": option_id}
            ).fetchall()

            for row in result:
                user_data = User(
                    user_id=str(row[0]), 
                    user_name=str(row[1])
                )
                user_list.append(user_data)
        return Participants(participants=user_list) if user_list else None
    
    def get_attend_option_id(self, event_id: int) -> int:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id AND o.option = '参加'"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                response = row[0]
        return response
    
    def get_option_id(self, event_id: int, option: str) -> Optional[int]:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id AND o.option = :option"),
                {"id": event_id, "option": option}
            ).fetchone()
        
        if result:
            return result[0]
        else:
            return None
    
    def is_option(self,user_id:str, option_id:int) -> Optional[bool]:
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT * FROM votes WHERE user_id = :user_id AND option_id = :option_id"),
                {"user_id": user_id, "option_id": option_id}
            ).fetchone()
            if result is None:
                return False
            return True
    
    def insert_vote(self, option_id:int, user_id:int):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                "INSERT INTO votes (option_id, user_id) VALUES (:option_id, :user_id)"),
                {"option_id": option_id, "user_id": user_id}
                )
  
    def delete_vote(self, option_id: int, user_id: int):
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(text(
                "DELETE FROM votes WHERE option_id = :option_id AND user_id = :user_id"),
                {"option_id": option_id, "user_id": user_id}
                )