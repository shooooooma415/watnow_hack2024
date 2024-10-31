from model.notification import Notification,EventData
from repository.event import Event
from repository.profile import Profile
from repository.get_attendance import GetAttendance
import firebase_admin
from firebase_admin import messaging,credentials
from main import today_event_id_list

cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
# cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

class SendNotification():
    def __init__(self,supabase_url: str) -> None:
        self.event = Event(supabase_url)
        self.profile = Profile(supabase_url)
        self.get_attendance = GetAttendance(supabase_url)
        
    def send_notification(self,event_id: int) -> None:
        event = self.event.get_event(event_id)
        option_id_list = self.get_attendance.get_attend_option_id(event_id)
        token_list = self.profile.get_token(option_id_list)
        
        notification = Notification(
            title=event.title,
            body=f"集合場所: {event.location_name}, 集合時間: {event.start_date_time.strftime('%H:%M')}"
            )
        
        data = EventData(
            content = "remind",
            event_id=str(event.id),
            title=event.title,
            location=event.location_name,
            latitude=str(event.latitude),
            longitude=str(event.longitude),
            start_time=str(event.start_date_time.strftime('%Y-%m-%d %H:%M:%S'))
            )
        
        message = messaging.MulticastMessage(
                data=data.model_dump(),
                tokens=token_list,
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body
                )
            )
        
        response = messaging.send_each_for_multicast(message)
        print(f"Success count: {response.success_count}")
        print(f"Failure count: {response.failure_count}")

        for idx, resp in enumerate(response.responses):
            if resp.success:
                print(f"Message {idx + 1} sent successfully")
            else:
                print(f"Message {idx + 1} failed with error: {resp.exception}")
    
    def send_messages(self):
        event_list = self.event.get_notification_event_id()
        for event_id in event_list:
            today_event_id_list.append(event_id)
            self.send_notification(event_id)
        return today_event_id_list