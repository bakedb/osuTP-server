from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn

from database import get_db, create_tables, User, Beatmap, Score
from models import (
    ScoreSubmission, UserCreate, UserResponse, BeatmapCreate, BeatmapResponse,
    ScoreResponse, LeaderboardEntry, GlobalRankingEntry
)
from scoring import (
    calculate_normal_value, calculate_custom_hit_value, calculate_final_value,
    calculate_global_rank_score
)

app = FastAPI(title="TP Server", description="Custom osu! server with unified scoring")

# Enable CORS for osu! client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/beatmaps", response_model=BeatmapResponse)
def create_beatmap(beatmap: BeatmapCreate, db: Session = Depends(get_db)):
    db_beatmap = db.query(Beatmap).filter(Beatmap.beatmap_id == beatmap.beatmap_id).first()
    if db_beatmap:
        return db_beatmap
    
    db_beatmap = Beatmap(**beatmap.dict())
    db.add(db_beatmap)
    db.commit()
    db.refresh(db_beatmap)
    return db_beatmap

@app.get("/api/beatmaps/{beatmap_id}", response_model=BeatmapResponse)
def get_beatmap(beatmap_id: int, db: Session = Depends(get_db)):
    beatmap = db.query(Beatmap).filter(Beatmap.beatmap_id == beatmap_id).first()
    if not beatmap:
        raise HTTPException(status_code=404, detail="Beatmap not found")
    return beatmap

@app.post("/api/scores/submit", response_model=ScoreResponse)
def submit_score(score_submission: ScoreSubmission, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == score_submission.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify or create beatmap
    beatmap = db.query(Beatmap).filter(Beatmap.beatmap_id == score_submission.beatmap_id).first()
    if not beatmap:
        # Create a basic beatmap entry if it doesn't exist
        beatmap = Beatmap(
            beatmap_id=score_submission.beatmap_id,
            title=f"Beatmap {score_submission.beatmap_id}",
            artist="Unknown",
            creator="Unknown",
            star_rating=1.0
        )
        db.add(beatmap)
        db.commit()
        db.refresh(beatmap)
    
    # Calculate scoring values
    normal_value = calculate_normal_value(
        score_submission.raw_score,
        score_submission.accuracy,
        beatmap.star_rating
    )
    custom_hit_value = calculate_custom_hit_value(
        score_submission.count_300,
        score_submission.count_100,
        score_submission.count_50
    )
    final_value = calculate_final_value(normal_value, custom_hit_value)
    
    # Create score record
    db_score = Score(
        user_id=score_submission.user_id,
        beatmap_id=beatmap.id,
        raw_score=score_submission.raw_score,
        accuracy=score_submission.accuracy,
        count_300=score_submission.count_300,
        count_100=score_submission.count_100,
        count_50=score_submission.count_50,
        count_miss=score_submission.count_miss,
        mods=score_submission.mods,
        normal_value=normal_value,
        custom_hit_value=custom_hit_value,
        final_value=final_value
    )
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return db_score

@app.get("/api/leaderboards/beatmap/{beatmap_id}", response_model=List[LeaderboardEntry])
def get_beatmap_leaderboard(beatmap_id: int, limit: int = 50, db: Session = Depends(get_db)):
    beatmap = db.query(Beatmap).filter(Beatmap.beatmap_id == beatmap_id).first()
    if not beatmap:
        raise HTTPException(status_code=404, detail="Beatmap not found")
    
    scores = db.query(Score).filter(Score.beatmap_id == beatmap.id)\
                          .order_by(Score.final_value.desc())\
                          .limit(limit).all()
    
    leaderboard = []
    for rank, score in enumerate(scores, 1):
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            user_id=score.user_id,
            username=score.user.username,
            final_value=score.final_value,
            timestamp=score.timestamp
        ))
    
    return leaderboard

@app.get("/api/leaderboards/global", response_model=List[GlobalRankingEntry])
def get_global_leaderboard(limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).all()
    
    global_rankings = []
    for user in users:
        # Get all final values for this user
        scores = db.query(Score.final_value).filter(Score.user_id == user.id).all()
        final_values = [score[0] for score in scores]
        
        # Calculate global rank score
        global_score = calculate_global_rank_score(final_values)
        
        global_rankings.append(GlobalRankingEntry(
            rank=0,  # Will be set after sorting
            user_id=user.id,
            username=user.username,
            global_score=global_score,
            score_count=len(final_values)
        ))
    
    # Sort by global score and assign ranks
    global_rankings.sort(key=lambda x: x.global_score, reverse=True)
    for rank, entry in enumerate(global_rankings, 1):
        entry.rank = rank
    
    return global_rankings[:limit]

@app.get("/api/users/{user_id}/scores", response_model=List[ScoreResponse])
def get_user_scores(user_id: int, limit: int = 100, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    scores = db.query(Score).filter(Score.user_id == user_id)\
                          .order_by(Score.final_value.desc())\
                          .limit(limit).all()
    
    return scores

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "message": "TP Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)