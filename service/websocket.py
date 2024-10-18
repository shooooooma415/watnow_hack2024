from repository.get_event import GetEvent,Location
from repository.get_profile import GetProfile
from repository.get_distance import GetDistance
from math import radians, sin, cos, sqrt, atan2
from sqlalchemy import create_engine
from typing import Optional,List,Dict
from datetime import datetime, timedelta
import json

class WebSocketService:
    def __init__(self,supabase_url:str):
        self.engine = create_engine(supabase_url)
        self.get_event = GetEvent(supabase_url)
        self.get_profile = GetProfile(supabase_url)
        self.get_distance = GetDistance(supabase_url)
    
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
        response = round(distance, 1)
        return response
    
    async def send_ranking(self, websocket):
        # get_all_distanceメソッドを呼び出して、辞書データを取得
        distance_dict = self.get_distance.get_all_distance()

        # ユーザーIDと距離のリストを作成し、距離でソート
        sorted_distances = sorted(
            [{"user_id": user_id, "distance": distance} for user_id, distance in distance_dict.items()],
            key=lambda x: x['distance'], reverse=True
        )

        # ランキング情報を作成
        ranking = [
            {
                "position": idx + 1,
                "user_id": user['user_id'],
                "name": self.get_profile.get_name(user['user_id']),  # 同期メソッドであればそのまま使用
                "alias": None,  # 必要に応じて `alias` を設定
                "distance": user['distance']
            }
            for idx, user in enumerate(sorted_distances)
        ]

        # WebSocketで送信するメッセージ
        ranking_message = {
            "action": "ranking_update",
            "ranking": ranking
        }

        # WebSocketでランキング情報を送信
        await websocket.send_text(json.dumps(ranking_message, ensure_ascii=False))

        
    def calculate_deadline(self,event_id:str) -> Optional[datetime]:
        start_time = self.get_event.get_start_time(event_id)
        deadline_time = start_time + timedelta(hours=3)
        return deadline_time