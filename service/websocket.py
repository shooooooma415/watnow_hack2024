from repository.get_event import GetEvent
from sqlalchemy import create_engine

class websocket:
    def __init__(self,supabase_url:str):
        self.engine = create_engine(supabase_url)
        self.get_event = GetEvent(supabase_url)
    
    def calculate_distance(self,event_id:str):
        self.get_event.get_location(event_id)