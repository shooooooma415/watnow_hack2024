import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime,date,timedelta,timezone
from sqlalchemy import create_engine, text
import os
from typing import List

# cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


class PushService():
    def __init__(self, supabase_url: str) -> None:
        self.engine = create_engine(supabase_url)

    def get_event_id(self) -> List[int]:
        dt_now = datetime.now(timezone.utc)
        dt_2days_later = dt_now + timedelta(days=2)
        lower = dt_now.replace(hour=23, minute=59, second=59)
        upper = dt_2days_later.replace(hour=0, minute=0, second=0)
        print(text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper})
        with self.engine.connect() as conn:
            query = conn.execute(
                text("SELECT id FROM events WHERE :lower < start_date_time AND start_date_time < :upper"),
                {"lower": lower, "upper": upper}
            )
            result = query.fetchall()
            print(f"クエリ結果: {result}")
            notification_event_id_list = [row[0] for row in result]
        
        return notification_event_id_list
    
    def get_option_id(self, event_id: int) -> List[int]:
        option_id_list = []
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT o.id FROM events e JOIN options o ON e.id = o.event_id WHERE e.id = :id AND o.option = '参加'"),
                {"id": event_id}
            ).fetchall()
            
            for row in result:
                option_id_list.append(row[0])
        
        print(f"取得したオプションIDリスト: {option_id_list}")
        return option_id_list


    
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
        print(f"取得したトークンリスト: {token_list}")
        return token_list


        
    
    def send_notification(self, event_id: int):
        with self.engine.connect() as conn:
            query = conn.execute(
                text("SELECT title FROM events WHERE id = :id"),
                {"id": event_id}
            ).mappings()
            
            result = query.fetchone()
            event_title = result['title']
            token_list = self.get_token(self.get_option_id(event_id))
            print(f"取得したトークンリスト: {token_list}")

            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=event_title,
                    body=f'明日は{event_title}です！'
                ),
                tokens=token_list
            )
            response = messaging.send_multicast(message)
            print(f"送信結果: {response}")
            return response