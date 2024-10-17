from service.notification import Notification
import os
import requests
# from main import today_event_id_list


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
        return response
    
    def send_event_ids(self,today_event_id_list:list[str]):
        event_id_list = self.notification.send_messages(today_event_id_list)
        
        for event_id in event_id_list:
            self.send_event_id(event_id)
        return event_id_list
            
# notification_service = NotificationService(supabase_url, SERVER_URL)
# notification_service.send_event_ids(today_event_id_list)