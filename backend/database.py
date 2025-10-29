"""
Database Models and Connection
Uses SQLAlchemy with PostgreSQL (Neon, Railway, etc.)
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Video(Base):
    """Video model"""
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    storage_key = Column(String, nullable=True)  # S3 key if uploaded to cloud
    local_path = Column(String, nullable=True)   # Local path if not using cloud
    size = Column(Integer, nullable=False)
    source_type = Column(String, nullable=False)  # 'upload', 'youtube', 'url'
    source_url = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class Job(Base):
    """Processing job model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    user_email = Column(String, index=True, nullable=False)
    video_id = Column(Integer, nullable=True)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    progress = Column(Integer, default=0)
    message = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    
    # Processing parameters
    num_clips = Column(Integer, default=5)
    clip_duration = Column(Integer, default=30)
    resolution = Column(String, default="portrait")
    
    # Results
    transcription = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class Clip(Base):
    """Generated clip model"""
    __tablename__ = "clips"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, index=True, nullable=False)
    clip_number = Column(Integer, nullable=False)
    
    # Storage
    storage_key = Column(String, nullable=True)  # S3 key
    local_path = Column(String, nullable=True)   # Local path (fallback)
    
    # Metadata
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    text = Column(Text, nullable=True)
    hook = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    virality_score = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# Database connection
_engine = None
_SessionLocal = None


def init_database(database_url: str):
    """
    Initialize database connection
    
    Args:
        database_url: PostgreSQL connection string
                     e.g., postgresql://user:pass@host:5432/dbname
    """
    global _engine, _SessionLocal
    
    try:
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10
        )
        
        # Create tables
        Base.metadata.create_all(bind=_engine)
        
        # Create session factory
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def get_db() -> Session:
    """
    Get database session
    
    Usage:
        db = get_db()
        try:
            # Use db
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    return _SessionLocal()


def is_database_enabled() -> bool:
    """Check if database is configured"""
    return _engine is not None
