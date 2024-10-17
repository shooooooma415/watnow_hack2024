from service.notification import Notification
from config import today_event_id_list
import os
import requests

# SERVER_URL = "http://127.0.0.1:8000"
SERVER_URL = "https://watnow-hack2024.onrender.com"
supabase_url = os.getenv('SUPABASE_URL')
notification=Notification(supabase_url)

class NotificationService:
    def __init__(self, supabase_url: str, server_url: str):
        self.notification = Notification(supabase_url)
        self.server_url = server_url

    def send_event_id(self, event_id: int):
        response = requests.post(f"{self.server_url}/events/id", json={"event_id": event_id})
        print(response.json())

    def send_event_ids(self):
        event_id_list = self.notification.send_messages()
        
        for event_id in event_id_list:
            self.send_event_id(event_id)
            
notification_service = NotificationService(supabase_url, SERVER_URL)
notification_service.send_event_ids()