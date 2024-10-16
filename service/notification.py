from repository.get_event import GetEvent
from repository.get_profile import GetProfile
import firebase_admin
from firebase_admin import messaging,credentials

# cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

class Notification():
    def __init__(self,supabase_url: str) -> None:
        self.get_event = GetEvent(supabase_url)
        self.get_profile = GetProfile(supabase_url)
        
    def send_notification(self,event_id: int):
        event_title = self.get_event.get_event_title(event_id)
        option_id_list = self.get_event.get_attend_option_id(event_id)
        token_list = self.get_profile.get_token(option_id_list)
        
        message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=event_title,
                    body=f'明日は{event_title}です！'
                ),
                tokens=token_list
            )
        response = messaging.send_multicast(message)
        return response
    
    def send_messages(self):
        event_id_list = self.get_event.get_notification_event_id()
        response_list = []
        for event_id in event_id_list:
            response = self.send_notification(event_id)
            response_list.append(response)
        return response_list