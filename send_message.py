from service.notification import Notification
import os
import requests
from main import today_event_id_list

SERVER_URL = "http://127.0.0.1:8000"


supabase_url = os.getenv('SUPABASE_URL')
notification=Notification(supabase_url)

# def send_event_id(event_id: int):
#     response = requests.post(f"{SERVER_URL}/events/id", json={"event_id": event_id})
#     return response

t = notification.send_messages()
print(t)
# for id in event_id_list:
#     send_event_id(id)
    
# print(today_event_id_list)