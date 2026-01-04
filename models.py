from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScoreSubmission(BaseModel):
    user_id: int
    beatmap_id: int
    raw_score: int
    accuracy: float
    count_300: int
    count_100: int
    count_50: int
    count_miss: int
    mods: Optional[str] = ""

class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BeatmapCreate(BaseModel):
    beatmap_id: int
    title: str
    artist: str
    creator: str
    star_rating: float

class BeatmapResponse(BaseModel):
    id: int
    beatmap_id: int
    title: str
    artist: str
    creator: str
    star_rating: float
    
    class Config:
        from_attributes = True

class ScoreResponse(BaseModel):
    id: int
    user_id: int
    beatmap_id: int
    raw_score: int
    accuracy: float
    count_300: int
    count_100: int
    count_50: int
    count_miss: int
    mods: str
    normal_value: float
    custom_hit_value: float
    final_value: float
    timestamp: datetime
    user: UserResponse
    beatmap: BeatmapResponse
    
    class Config:
        from_attributes = True

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    final_value: float
    timestamp: datetime

class GlobalRankingEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    global_score: float
    score_count: int
