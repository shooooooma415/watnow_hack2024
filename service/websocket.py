from repository.get_event import GetEvent,Location
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy import create_engine
from typing import Optional,List,Dict
from datetime import datetime, timedelta
import json

class WebSocketService:
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
    
    def calculate_distance(self, event_id: str, user_location: Location) -> Optional[float]:

        event_location = self.get_event.get_location(event_id)
        
        if event_location.latitude is None or event_location.longitude is None:
            raise ValueError(f"Event {event_id} has invalid location data")
        
        if user_location.latitude is None or user_location.longitude is None:
            raise ValueError("User location data is incomplete")
        
        distance = self.haversine_distance(
            user_location.latitude, user_location.longitude,
            event_location.latitude, event_location.longitude
        )
        
        return distance
    
    async def send_ranking(self, websocket, user_distances: List[Dict[str, float]]):
        sorted_distances = sorted(user_distances, key=lambda x: x['distance'], reverse=True)
        ranking = [
            {
                "position": idx + 1,
                "user_id": user['user_id'],
                "alias": None,
                "distance": user['distance']
            }
            for idx, user in enumerate(sorted_distances)
        ]
        ranking_message = {
            "action": "ranking_update",
            "ranking": ranking
        }
        await websocket.send_text(json.dumps(ranking_message))
        
    def calculate_deadline(self,event_id:str) -> Optional[datetime]:
        start_time = self.get_event.get_start_time(event_id)
        deadline_time = start_time + timedelta(hours=3)
        return deadline_time