from typing import Optional,List,Dict
from pydantic import BaseModel

class TimeRankingComponent(BaseModel):
    id: int
    position: int
    name: str
    alias: Optional[str]
    time: int
    
class CountRankingComponent(BaseModel):
    id: int
    position: int
    name: str
    alias: Optional[str]
    count: int
    
class PointRankingComponent(BaseModel):
    id: int
    position: int
    name: str
    alias: Optional[str]
    point: int

class TimeRanking(BaseModel):
    ranking:List[TimeRankingComponent]
    
class CountRanking(BaseModel):
    ranking:List[CountRankingComponent]
    
class PointRanking(BaseModel):
    ranking:List[PointRankingComponent]