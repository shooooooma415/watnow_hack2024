from service.notification import Notification
import os
import requests

SERVER_URL = "http://127.0.0.1:8000"


supabase_url = os.getenv('SUPABASE_URL')
notification=Notification(supabase_url)

def send_event_id(event_id: int):
    response = requests.post(f"{SERVER_URL}/events/id", json={"event_id": event_id})
    return response

event_id_list = notification.send_messages()

for id in event_id_list:
    send_event_id(id)