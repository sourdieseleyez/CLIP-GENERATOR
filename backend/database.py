"""
Database Models and Connection
Uses SQLAlchemy with PostgreSQL (Neon, Railway, etc.)
"""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Try to import SQLAlchemy - it's optional
try:
    from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session, relationship
    import enum
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.warning("SQLAlchemy not installed - database features disabled. Install with: pip install sqlalchemy psycopg[binary]")

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
else:
    Base = None


if SQLALCHEMY_AVAILABLE:
    class UserRole(enum.Enum):
        """User role types"""
        CLIENT = "client"      # Posts campaigns, pays for clips
        CLIPPER = "clipper"    # Creates clips, earns money
        BOTH = "both"          # Can do both
    
    class UserTier(enum.Enum):
        """Clipper performance tiers"""
        BRONZE = "bronze"      # 70/30 split
        SILVER = "silver"      # 75/25 split
        GOLD = "gold"          # 80/20 split
        PLATINUM = "platinum"  # 85/15 split

    class User(Base):
        """User model"""
        __tablename__ = "users"
        
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True, nullable=False)
        hashed_password = Column(String, nullable=False)
        disabled = Column(Boolean, default=False)
        
        # Marketplace fields
        role = Column(Enum(UserRole), default=UserRole.BOTH)
        tier = Column(Enum(UserTier), default=UserTier.BRONZE)
        
        # Clipper stats
        total_earnings = Column(Float, default=0.0)
        total_clips = Column(Integer, default=0)
        total_views = Column(Integer, default=0)
        rating = Column(Float, default=5.0)
        rating_count = Column(Integer, default=0)
        
        # Profile
        display_name = Column(String, nullable=True)
        bio = Column(Text, nullable=True)
        portfolio_url = Column(String, nullable=True)
        
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
else:
    User = None
    UserRole = None
    UserTier = None


if SQLALCHEMY_AVAILABLE:
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
else:
    Video = None


if SQLALCHEMY_AVAILABLE:
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
else:
    Job = None


if SQLALCHEMY_AVAILABLE:
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
        
        # Analytics & Performance Tracking
        views = Column(Integer, default=0)
        revenue = Column(Float, default=0.0)  # In dollars
        platform = Column(String, nullable=True)  # 'tiktok', 'youtube', 'instagram', etc.
        posted_at = Column(DateTime, nullable=True)
        last_updated = Column(DateTime, nullable=True)
        
        created_at = Column(DateTime, default=datetime.utcnow)
else:
    Clip = None


if SQLALCHEMY_AVAILABLE:
    class CampaignStatus(enum.Enum):
        """Campaign status"""
        DRAFT = "draft"
        ACTIVE = "active"
        PAUSED = "paused"
        COMPLETED = "completed"
        CANCELLED = "cancelled"

    class Campaign(Base):
        """Campaign model - clients post these to hire clippers"""
        __tablename__ = "campaigns"
        
        id = Column(Integer, primary_key=True, index=True)
        client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        
        # Campaign details
        title = Column(String, nullable=False)
        description = Column(Text, nullable=False)
        video_url = Column(String, nullable=False)  # Source video
        
        # Requirements
        num_clips_needed = Column(Integer, default=5)
        clip_duration = Column(Integer, default=30)
        resolution = Column(String, default="portrait")
        style_notes = Column(Text, nullable=True)
        
        # Budget
        budget_per_clip = Column(Float, nullable=False)  # In dollars
        total_budget = Column(Float, nullable=False)
        
        # Status
        status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
        clips_submitted = Column(Integer, default=0)
        clips_approved = Column(Integer, default=0)
        
        # Dates
        deadline = Column(DateTime, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)
else:
    Campaign = None
    CampaignStatus = None


if SQLALCHEMY_AVAILABLE:
    class MarketplaceJobStatus(enum.Enum):
        """Marketplace job status"""
        CLAIMED = "claimed"        # Clipper claimed the job
        IN_PROGRESS = "in_progress"  # Clipper is working
        SUBMITTED = "submitted"    # Waiting for client review
        APPROVED = "approved"      # Client approved, ready for payout
        REJECTED = "rejected"      # Client rejected
        PAID = "paid"             # Clipper has been paid

    class MarketplaceJob(Base):
        """Marketplace job - links campaigns to clippers"""
        __tablename__ = "marketplace_jobs"
        
        id = Column(Integer, primary_key=True, index=True)
        campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
        clipper_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        clip_id = Column(Integer, ForeignKey('clips.id'), nullable=True)
        
        # Status
        status = Column(Enum(MarketplaceJobStatus), default=MarketplaceJobStatus.CLAIMED)
        
        # Payment
        agreed_price = Column(Float, nullable=False)
        clipper_share = Column(Float, nullable=False)  # After platform fee
        platform_fee = Column(Float, nullable=False)
        
        # Review
        client_feedback = Column(Text, nullable=True)
        client_rating = Column(Integer, nullable=True)  # 1-5 stars
        
        # YouTube tracking
        youtube_video_id = Column(String, nullable=True)
        youtube_url = Column(String, nullable=True)
        tracking_code = Column(String, unique=True, nullable=True)
        
        # Dates
        claimed_at = Column(DateTime, default=datetime.utcnow)
        submitted_at = Column(DateTime, nullable=True)
        approved_at = Column(DateTime, nullable=True)
        paid_at = Column(DateTime, nullable=True)
else:
    MarketplaceJob = None
    MarketplaceJobStatus = None


if SQLALCHEMY_AVAILABLE:
    class PayoutStatus(enum.Enum):
        """Payout status"""
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

    class Payout(Base):
        """Payout model - tracks payments to clippers"""
        __tablename__ = "payouts"
        
        id = Column(Integer, primary_key=True, index=True)
        clipper_id = Column(Integer, ForeignKey('users.id'), nullable=False)
        
        # Amount
        amount = Column(Float, nullable=False)
        currency = Column(String, default="USD")
        
        # Jobs included in this payout
        job_ids = Column(Text, nullable=False)  # JSON array of job IDs
        
        # Status
        status = Column(Enum(PayoutStatus), default=PayoutStatus.PENDING)
        
        # Payment method (for future Stripe integration)
        payment_method = Column(String, default="manual")
        transaction_id = Column(String, nullable=True)
        
        # Dates
        requested_at = Column(DateTime, default=datetime.utcnow)
        processed_at = Column(DateTime, nullable=True)
        completed_at = Column(DateTime, nullable=True)
else:
    Payout = None
    PayoutStatus = None


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
    
    if not SQLALCHEMY_AVAILABLE:
        logger.error("SQLAlchemy not installed. Install with: pip install sqlalchemy psycopg[binary]")
        return False
    
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


def get_db():
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
