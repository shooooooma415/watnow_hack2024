import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime,date,timedelta
from sqlalchemy import create_engine, text
import os
from typing import List

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


class PushService():
    def __init__(self, supabase_url: str):
        self.engine = create_engine(supabase_url)

    def filter_events_by_remaining_time(self) -> List:
        dt_now = datetime.datetime.now()
        ten_hours = timedelta(hours=10)
        notification_event_id_list = list()
        with self.engine.connect() as conn:
            query = conn.execute(text("SELECT id, start_date_time FROM events"))
            events_dict = {
                row['start_date_time']: datetime.combine(date.today(), row['id']) 
                for row in query
            }
        for start_time in events_dict.keys():
            limit_time = start_time - dt_now
            if (limit_time < ten_hours):
                 notification_event_id_list.append(events_dict[start_time])
        return notification_event_id_list
    
    def get_unsent_notifications(self) -> List:
        event_id_list = list()
        for id in self.filter_events_by_remaining_time():
            with self.engine.connect() as conn:
                result = conn.execute(
                        text("SELECT id FROM events WHERE id = :id AND is_notification = True"),
                        {'id': id}
                )
                for row in result:
                    event_id_list.append(row['id'])
        return event_id_list
    
    def fetch_applicable_auth_id(self)-> List:
        option_id_list = list()
        user_id_list = list()
        for id in self.fetch_applicable_auth_id():
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id FROM options WHERE event_id = :id AND title = :title"),
                    {'id':id, 'title':"参加"}
                )
                for row in result:
                    option_id_list.append(row['id'])
        
        for id in option_id_list:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT user_id FROM votes WHERE option_id = :id"),
                    {'id': id}
                )
                for row in result:
                    user_id_list.append(row['id'])
                    
        for id in user_id_list:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT auth_id FROM users WHERE id = :id"),
                    {'id': id}
                )
                for row in result:
                    user_id_list.append(row['id'])
        return user_id_list
    
    def send_push_notifications(self):
        token_list = self.fetch_applicable_auth_id()
        event_id_list = self.get_unsent_notifications
        event_title_list = list()
        for id in event_id_list:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT title FROM events WHERE id = :id"),
                    {'id': id}
                )
                for row in result:
                    event_title_list.append(row['id'])
         
        for event_title in event_id_list:           
            for token in token_list:
                message = messaging.Message(
                    notification=messaging.Notification(
                    title = event_title,
                    body ='明日は' + event_title + "です！",
                ),
                token = token,
            )
                response = messaging.send(message)
        return response
        
    
    
    
    