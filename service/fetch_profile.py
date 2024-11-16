from model.profile import Delay,UserProfile
from model.aliase import AliaseID
from repository.profile import Profile
from datetime import timedelta
from typing import Optional,Dict,Tuple


class ProfileService():
    def __init__(self, supabase_url: str) -> None:
        self.profile = Profile(supabase_url)
        
        self.alias_points = {
            AliaseID.遅刻王: 401,
            AliaseID.CTO: 101,
            AliaseID.遅刻インターン生: 21,
            AliaseID.ビギナー遅刻者: 1,
            AliaseID.健常者:-1,
            AliaseID.watnowの光:-51,
            AliaseID.無遅刻ゴールド:-101
        }
        
    def calculate_late_time(self,user_id:int) -> Optional[Delay]:
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

    def calculate_late_point(self, user_id: int) -> Optional[int]:
        plus_total = 0
        minus_total = 0
        p_count = 0
        m_count = 0

        for delay in self.profile.get_all_delay_time(user_id):
            delay_minutes = delay.total_seconds() / 60
            if delay_minutes > 0:
                plus_total += delay_minutes
                p_count += 1
            else:
                minus_total += abs(delay_minutes)
                m_count += 1

        
        late_point = int(
            plus_total * (1 + 0.5 * (p_count - 1)) - minus_total * (1 + 0.2 * (m_count - 1))
        )
        
        return late_point

    
    def judge_aliase(self,user_id) -> Optional[int]:
        tikoku_point = self.calculate_late_point(user_id)
        if tikoku_point <= -101:
            return AliaseID.無遅刻ゴールド.value
        elif -100 <= tikoku_point <= -51:
            return AliaseID.watnowの光.value
        elif -50 <=tikoku_point <= -1:
            return AliaseID.健常者.value
        elif tikoku_point == 0:
            return AliaseID.遅刻1回生.value
        elif 1 <= tikoku_point <= 20:
            return AliaseID.ビギナー遅刻者.value
        elif 21 <= tikoku_point <= 100:
            return AliaseID.遅刻インターン生.value
        elif 101 <= tikoku_point <= 400:
            return AliaseID.CTO.value
        elif tikoku_point >= 401:
            return AliaseID.遅刻王.value
    
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
        
    def fetch_point_and_tokens(self,option_id:int) -> Dict[str,int]:
        point_token_dict = {}
        token_dict = self.profile.get_remind_tokens_for_aliased_users(option_id)
        
        for user_id,token in token_dict.items():
            point = self.calculate_late_point(user_id)
            point_token_dict[token] = point
            
        return point_token_dict
    
    def find_next_alias(self,tikoku_point:int) -> Optional[str]:
        for alias, points_required in sorted(self.alias_points.items(), key=lambda x: x[1]):
            if tikoku_point < points_required:
                return alias.name
        
        return alias.遅刻王
    
    def calculate_required_delay_time(self, user_id:int) -> Tuple[str, int]:
        
        delay_times = self.profile.get_all_delay_time(user_id)
        
        plus_total = 0
        minus_total = 0
        p_count = 0
        m_count = 0

        for delay in delay_times:
            delay_minutes = delay.total_seconds() / 60
            if delay_minutes > 0:
                plus_total += delay_minutes
                p_count += 1
            else:
                minus_total += abs(delay_minutes)
                m_count += 1
                
        late_point = int(
            plus_total * (1 + 0.5 * (p_count - 1)) - minus_total * (1 + 0.2 * (m_count - 1))
        )
        
        next_aliase = self.find_next_alias(late_point)
        next_aliase_point = self.alias_points[AliaseID[next_aliase]]
        
        required_delay_time = (next_aliase_point + minus_total*(1+0.2*(m_count-1)))/1 + 0.5 * p_count
        
        return next_aliase, int(required_delay_time)