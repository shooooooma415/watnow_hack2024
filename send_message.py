from service.notification import Notification
import os

supabase_url = os.getenv('SUPABASE_URL')
notification=Notification(supabase_url)

notification.send_messages()