from typing import Optional,List,Dict
from pydantic import BaseModel

class TimeRankingComponent(BaseModel):
    id: int
    position: int
    name: str
    alias: Optional[str]
    time: int
    

class TimeRanking(BaseModel):
    ranking:List[TimeRankingComponent]