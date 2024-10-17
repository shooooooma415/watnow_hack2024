from model.event import User,Participants
from sqlalchemy import create_engine, text
from typing import List,Dict,Optional

class GetAttendance():
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
    
    def get_attend_option_id(self, event_id: int) -> List[int]:
        option_id_list = []
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id AND o.option = '参加'"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                option_id_list.append(row[0])
        return option_id_list
    
    def get_option_id(self,event_id:str):
        option_id_list = []
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                option_id_list.append(row[0])
        return option_id_list
    
    def verify_vote(self,user_id:str,option_id_list:list[int]) -> Optional[bool]:
        pass