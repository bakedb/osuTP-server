from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scores = relationship("Score", back_populates="user")

class Beatmap(Base):
    __tablename__ = "beatmaps"
    
    id = Column(Integer, primary_key=True, index=True)
    beatmap_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    artist = Column(String)
    creator = Column(String)
    star_rating = Column(Float)
    
    scores = relationship("Score", back_populates="beatmap")

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    beatmap_id = Column(Integer, ForeignKey("beatmaps.id"))
    
    # Original score data
    raw_score = Column(Integer)
    accuracy = Column(Float)
    count_300 = Column(Integer)
    count_100 = Column(Integer)
    count_50 = Column(Integer)
    count_miss = Column(Integer)
    mods = Column(String)
    
    # Computed values
    normal_value = Column(Float)
    custom_hit_value = Column(Float)
    final_value = Column(Float)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="scores")
    beatmap = relationship("Beatmap", back_populates="scores")

# Database setup
engine = create_engine("sqlite:///./tpserver.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
