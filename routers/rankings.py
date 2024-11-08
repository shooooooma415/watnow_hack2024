from fastapi import APIRouter
from model.rankings import TimeRanking,CountRanking
from service.fetch_ranking import FetchRanking


def get_rankings_router(supabase_url:str):
    router = APIRouter(prefix="/rankings", tags=["Ranking"])
    fetch_ranking = FetchRanking(supabase_url)
    
    @router.get("/point")
    def get_point_ranking():
        pass
    
    @router.get("/count",response_model=CountRanking)
    def get_count_ranking():
        return fetch_ranking.sort_count_ranking()
    
    @router.get("/time",response_model=TimeRanking)
    def get_time_ranking():
        return fetch_ranking.sort_time_ranking()
    
    return router