from model.profile import Delay
from model.rankings import TimeRanking,TimeRankingComponent
from repository.profile import Profile
from service.fetch_profile import ProfileService
from typing import Dict,Optional

class FetchRanking():
    def __init__(self,supabase_url:str) -> None:
        self.profile = Profile(supabase_url)
        self.profile_service = ProfileService(supabase_url)
        
    def get_delay_dict(self) -> Dict[int,Delay]:
        user_time_dict = {}
        user_ids = self.profile.get_all_user_id()
        for user_id in user_ids:
            delay_info = self.profile_service.calculate_late_time(user_id)
            user_time_dict[user_id] = delay_info
        return user_time_dict
    
    def sort_time_ranking(self,limit: int = 3) -> Optional[TimeRanking]:
        user_time_dict = self.get_delay_dict()
        
        sorted_user_time = sorted(
        user_time_dict.items(),
        key=lambda item: item[1].total_late_time if item[1] else 0,
        reverse=True
        )

        ranking_list = []
        current_rank = 0
        previous_time = None
        skip = 1
        count = 0

        for user_id, delay_info in sorted_user_time:
            if delay_info is None:
                continue

            if limit and count >= limit and delay_info.total_late_time != previous_time:
                break

            if delay_info.total_late_time != previous_time:
                current_rank += skip
                rank = current_rank
                skip = 1
            else:
                rank = current_rank
                skip += 1

            ranking_component = TimeRankingComponent(
                id=user_id,
                position=rank,
                name=self.profile.get_name(user_id),
                alias=self.profile.get_aliase(user_id) or "No alias",
                time=delay_info.total_late_time
            )
            ranking_list.append(ranking_component)

            previous_time = delay_info.total_late_time
            count += 1

        return TimeRanking(ranking=ranking_list)