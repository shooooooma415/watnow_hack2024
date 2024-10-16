from model.profile import Delay,Profile
from repository.get_profile import GetProfile
from datetime import timedelta
import datetime
from typing import Optional

class ProfileService():
  def __init__(self, supabase_url: str) -> None:
    self.get_profile = GetProfile(supabase_url)
      
  def calculate_late_time(self,user_id) -> Delay:
    delay_time = self.get_profile.get_delay_time(user_id)
    
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
  
  def fetch_profile(self,user_id) -> Optional[Profile]:
      alias = self.get_profile.get_aliase(user_id)
      name = self.get_profile.get_name(user_id)
      late_info = self.calculate_late_time(user_id)
      
      return Profile(
        name=name,
        alias=alias,
        late_count=late_info.late_count,
        total_late_time=late_info.total_late_time,
        late_percentage=late_info.late_percentage,
        on_time_count=late_info.on_time_count
      )
