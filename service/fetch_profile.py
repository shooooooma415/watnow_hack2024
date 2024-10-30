from model.profile import Delay,UserProfile
from repository.profile import Profile
from datetime import timedelta
import datetime
from typing import Optional

class ProfileService():
    def __init__(self, supabase_url: str) -> None:
        self.profile = Profile(supabase_url)
        
    def calculate_late_time(self,user_id) -> Optional[Delay]:
        delay_time = self.profile.get_delay_time(user_id)

        if delay_time is None:
            none_response = Delay(total_late_time = 0, 
                        late_count = 0, 
                        on_time_count = 0, 
                        late_percentage = 0)
            return none_response

        late_p=0
        on_time_p=0
        total_late = timedelta(seconds=0)

        for time in delay_time:
            if time < timedelta(seconds=0):
                on_time_p += 1
            else:
                late_p += 1
                total_late += time
            
        participate_count = late_p + on_time_p
        late_rate = late_p / participate_count *100

        total_late_minutes = int (total_late.total_seconds() / 60)

        return Delay(total_late_time = total_late_minutes, 
                        late_count = late_p, 
                        on_time_count = on_time_p, 
                        late_percentage = late_rate)

    def calculate_late_point(self,user_id:int) -> Optional[int]:
        plus_time=[]
        minus_time=[]
        delay_time_list = self.profile.get_all_delay_time(user_id)

        for i in delay_time_list:
            if i > 0:
                plus_time.append(i)
            else:
                i = abs(i)
                minus_time.append(i)
        
        p_count = len(plus_time)
        m_count = len(minus_time)
        
        plus_total = sum(plus_time)
        minus_total = sum(minus_time)
        
        late_point = int(plus_total * (1 + 0.5 * (p_count - 1)) - minus_total * (1 + 0.2 * (m_count - 1)))
        
        return late_point
    
    def judge_aliase(self,user_id) -> Optional[int]:
        tikoku_point = self.calculate_late_point(user_id)
        if tikoku_point <= -101:
            return 9
        elif -100 <= tikoku_point <= -51:
            return 8
        elif -50 <=tikoku_point <= -1:
            return 7
        elif tikoku_point == 0:
            return 6
        elif 1 <= tikoku_point <= 20:
            return 5
        elif 21 <= tikoku_point <= 100:
            return 4
        elif 101 <= tikoku_point <= 400:
            return 3
        elif tikoku_point >= 401:
            return 2
    
    def fetch_profile(self,user_id) -> Optional[UserProfile]:
        alias = self.profile.get_aliase(user_id)
        name = self.profile.get_name(user_id)
        late_info = self.calculate_late_time(user_id)
        tikoku_point = self.calculate_late_point(user_id)

        return UserProfile(
            name=name,
            alias=alias,
            late_count=late_info.late_count,
            total_late_time=late_info.total_late_time,
            late_percentage=late_info.late_percentage,
            on_time_count=late_info.on_time_count,
            tikoku_point=tikoku_point
        )