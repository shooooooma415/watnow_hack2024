from repository.get_event import GetEvent
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy import create_engine

class websocket:
    def __init__(self,supabase_url:str):
        self.engine = create_engine(supabase_url)
        self.get_event = GetEvent(supabase_url)
    
    def haversine_distance(self,lat1:float, lon1:float, lat2:float, lon2:float) -> float:
        R = 6371.0
        
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance
    
    def calculate_distance(self,event_id:str):
        event_location = self.get_event.get_location(event_id)