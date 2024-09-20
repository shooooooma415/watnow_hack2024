import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime,date,timedelta
from sqlalchemy import create_engine, text
import os
from typing import List

cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
# cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


class PushService():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)

    def get_event_id(self) -> List[int]:
        dt_now = datetime.now()
        dt_2days_later = dt_now + timedelta(days=2)
        lower = dt_now.replace(hour=23, minute=59, second=59)
        upper = dt_2days_later.replace(hour=0, minute=0, second=0)
        
        with self.engine.connect() as conn:
            # 直接 datetime オブジェクトでクエリに渡す
            query = conn.execute(
                text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper}
            )
            notification_event_id_list = [row['id'] for row in query.fetchall()]
        
        return notification_event_id_list
    
    def get_option_id(self,event_id:str)->List[str]:
        option_id_list = list()
        with self.engine.connect() as conn:
            query = conn.execute(
                text("""SELECT 
                        o.id
                        FROM events e
                        JOIN options o
                        ON e.id = o.event_id
                        WHERE e.id = :id AND o.option = '参加'
                        """)),{
                            "id":event_id}
            for row in query:
                option_id_list.append(row['id'])
        return option_id_list
    
    def get_user_id(self, option_id:str)->List[str]:
        token_list = list()
        with self.engine.connect() as conn:
            query = conn.execute(
                text("""SELECT 
                        u.token
                        FROM votes v
                        JOIN users u
                        ON v.user_id = u.id
                        WHERE v.option_id = :id
                        """)),{
                            "id":option_id
                        }
            for row in query:
                token_list.append(row['id'])
        return token_list
    
    def send_notofication(self,event_id:str):
        with self.engine.connect() as conn:
            query = conn.execute(text("SELECT title FROM events WHERE id = :id")),{"id": event_id}
        result = query.fetchone()
        event_title = result['title']
        token_list = self.get_user_id(self.get_option_id(event_id))
        message = messaging.subscribe_to_topic(
                title = event_title,
                body ='明日は' + event_title + "です！",
        )
        response = messaging.send(token_list,message)
        
        return response