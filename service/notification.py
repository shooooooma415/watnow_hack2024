from repository.event import Event
from repository.profile import Profile
from repository.get_attendance import GetAttendance
import firebase_admin
from firebase_admin import messaging,credentials
from main import today_event_id_list

# cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


class Notification():
    def __init__(self,supabase_url: str) -> None:
        self.event = Event(supabase_url)
        self.profile = Profile(supabase_url)
        self.get_attendance = GetAttendance(supabase_url)
        
    def send_notification(self,event_id: int):
        event_title = self.event.get_event_title(event_id)
        option_id_list = self.get_attendance.get_attend_option_id(event_id)
        token_list = self.profile.get_token(option_id_list)
        
        print("fcm_list",token_list)
        
        message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=event_title,
                    body=f'明日は{event_title}です！'
                ),
                tokens=token_list
            )
        response = messaging.send_each_for_multicast(message)
        print(f"Success count: {response.success_count}")
        print(f"Failure count: {response.failure_count}")

        # 各メッセージの結果を表示
        for idx, resp in enumerate(response.responses):
            if resp.success:
                print(f"Message {idx + 1} sent successfully")
            else:
                print(f"Message {idx + 1} failed with error: {resp.exception}")
        print(response)
    
    def send_messages(self):
        event_list = self.event.get_notification_event_id()
        for event_id in event_list:
            today_event_id_list.append(event_id)
            self.send_notification(event_id)
        return today_event_id_list