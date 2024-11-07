from model.notification import Notification,RemindData,AliaseData
from repository.event import Event
from repository.profile import Profile
from repository.get_attendance import GetAttendance
from service.fetch_profile import ProfileService
import firebase_admin
from firebase_admin import messaging,credentials

cred = credentials.Certificate("/etc/secrets/serviceAccountKey.json")
# cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

class SendNotification():
    def __init__(self,supabase_url: str) -> None:
        self.event = Event(supabase_url)
        self.profile = Profile(supabase_url)
        self.get_attendance = GetAttendance(supabase_url)
        self.profile_service = ProfileService(supabase_url)
        
    def send_remind(self,event_id: int) -> None:
        event = self.event.get_event(event_id)
        option_id_list = self.get_attendance.get_attend_option_id(event_id)
        token_list = self.profile.get_remind_tokens(option_id_list)
        
        notification = Notification(
            title=f"明日は{event.title}です！",
            body=f"集合場所: {event.location_name}, 集合時間: {event.start_date_time.strftime('%H:%M')}"
            )
        
        data = RemindData(
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
    
    async def send_remind_all_events(self):
        event_list = self.event.get_notification_event_id()
        
        for event_id in event_list:
            print(f"Sending reminder for event ID: {event_id}")
            self.send_remind(event_id)
    
    def send_caution_remind(self, event_id: int):
        event = self.event.get_event(event_id)
        option_id_list = self.get_attendance.get_attend_option_id(event_id)
        token_point_dict = self.profile_service.fetch_point_and_tokens(option_id_list)
        
        notification_title = f"明日は{event.location_name}に{event.start_date_time.strftime('%H:%M')} 集合です！"
        
        for token, point in token_point_dict.items():
            notification = Notification(
                title=notification_title,
                body=f"あなたの今の遅刻ポイントは「{point}」です！明日は遅れないようにしましょう！！"
            )
            
            message = messaging.Message(
                token=token,
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body
                )
            )
            response = messaging.send(message)
            if response:
                print(f"Message to {token} sent successfully with point {point}")
            else:
                print(f"Message to {token} failed")

                
    async def send_caution_all_events(self):
        event_list = self.event.get_notification_event_id()
        for event_id in event_list:
            self.send_caution_remind(event_id)

    
    def send_renew_aliase(self,user_id:int):
        token = self.profile.get_token(user_id)
        aliase = self.profile.get_aliase(user_id)
        
        notification = Notification(
            title = f"「{aliase}」が付与されました",
            body = f"現在の称号は「{aliase}」です"
        )
        
        data = AliaseData(
            content = "aliase",
            aliase = aliase
        )
        
        message = messaging.Message(
                data=data.model_dump(),
                token=token,
                notification=messaging.Notification(
                    title=notification.title,
                    body=notification.body
                )
            )
        response = messaging.send(message)

        return response