from repository.event import Event,Location
from repository.profile import Profile
from repository.distance import Distance
from sqlalchemy import create_engine
from typing import Optional
from datetime import datetime, timedelta
import json
from geopy.distance import geodesic

class WebSocketService:
    def __init__(self,supabase_url:str):
        self.engine = create_engine(supabase_url)
        self.event = Event(supabase_url)
        self.profile = Profile(supabase_url)
        self.distance = Distance(supabase_url)
    
    def haversine_distance(self, lat1:float, lon1:float, lat2:float, lon2:float) -> float:
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
    
        return distance
    
    def calculate_distance(self, event_id: str, user_location: Location) -> Optional[float]:

        event_location = self.event.get_location(event_id)
        
        if event_location.latitude is None or event_location.longitude is None:
            raise ValueError(f"Event {event_id} has invalid location data")
        
        if user_location.latitude is None or user_location.longitude is None:
            raise ValueError("User location data is incomplete")
        
        distance = self.haversine_distance(
            user_location.latitude, user_location.longitude,
            event_location.latitude, event_location.longitude
        )
        response = round(distance, 1)
        return response
    
    async def send_ranking(self, websocket):
        distance_dict = self.distance.get_all_distance()
        sorted_distances = sorted(
            [{"user_id": user_id, "distance": distance/1000} for user_id, distance in distance_dict.items()],
            key=lambda x: x['distance'], reverse=True
        )
        ranking = [
            {
                "position": idx + 1,
                "user_id": user['user_id'],
                "name": self.profile.get_name(user['user_id']),
                "alias": None,
                "distance": user['distance']
            }
            for idx, user in enumerate(sorted_distances)
        ]

        ranking_message = {
            "action": "ranking_update",
            "ranking": ranking
        }
        await websocket.send_text(json.dumps(ranking_message, ensure_ascii=False))

        
    def calculate_deadline(self,event_id:str) -> Optional[datetime]:
        start_time = self.event.get_start_time(event_id)
        deadline_time = start_time + timedelta(hours=3)
        return deadline_time