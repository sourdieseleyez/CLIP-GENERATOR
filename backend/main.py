from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
import shutil
import uuid
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Configure logging FIRST before any imports that might use it
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from gemini_processor import GeminiVideoProcessor
from storage import init_storage, get_storage
from database import init_database, get_db, is_database_enabled, User as DBUser, Video as DBVideo, Job as DBJob, Clip as DBClip, Payout, PayoutStatus

# Optional queueing imports will be attempted later (lazy)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import marketplace router
try:
    from marketplace import router as marketplace_router
    MARKETPLACE_AVAILABLE = True
except ImportError:
    MARKETPLACE_AVAILABLE = False
    logger.warning("Marketplace module not available")

# Import YouTube integration
try:
    from youtube_integration import router as youtube_router
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("YouTube integration not available")

# Import admin router
try:
    from admin import router as admin_router
    ADMIN_AVAILABLE = True
except ImportError:
    ADMIN_AVAILABLE = False
    logger.warning("Admin module not available")

# Logging already configured above

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Clip Generator API",
    description="AI-powered video clip generation API with marketplace",
    version="2.0.0"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include marketplace router
if MARKETPLACE_AVAILABLE:
    app.include_router(marketplace_router)
    logger.info("✓ Marketplace endpoints enabled")

# Include YouTube router
if YOUTUBE_AVAILABLE:
    app.include_router(youtube_router)
    logger.info("✓ YouTube integration enabled")

# Include admin router
if ADMIN_AVAILABLE:
    app.include_router(admin_router)
    logger.info("✓ Admin endpoints enabled")

# CORS configuration
# Allow localhost dev ports by default; can opt-in to allow all origins with CORS_ALLOW_ALL env var
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "false").lower() in ("1", "true", "yes")
if CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Allow common dev ports and any localhost port via regex
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
        allow_origin_regex=r"^http://localhost(:[0-9]+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Import auth utilities
from auth import get_current_user, create_access_token, oauth2_scheme, SECRET_KEY, ALGORITHM

# Security
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Option to disable auth for local testing (set to 'true' in backend/.env)
# DEFAULT IS NOW FALSE - auth is enabled by default for production safety
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() in ("1", "true", "yes")

# Configure bcrypt with truncate_error=False to handle long passwords gracefully
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=False)
# oauth2_scheme is imported from auth module - don't redefine here

# Gemini API Key (using Flash Lite - 133x cheaper than GPT-4!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# STT engine selection: 'whisper' (local), 'faster-whisper' (if installed)
STT_ENGINE = os.getenv("STT_ENGINE", "whisper")
# Queueing config: set USE_QUEUE=true and REDIS_URL to enable Redis+RQ
USE_QUEUE = os.getenv("USE_QUEUE", "false").lower() in ("1", "true", "yes")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# Option to require Gemini processor for processing jobs. Set to 'false' to allow enqueueing
# jobs even when GEMINI_API_KEY is not set (dev/testing). Default is 'true' so the app treats
# Gemini as the main/required video processor.
REQUIRE_GEMINI = os.getenv("REQUIRE_GEMINI", "true").lower() in ("1", "true", "yes")

# Initialize video processor with Gemini 2.5 Flash Lite
video_processor = GeminiVideoProcessor(GEMINI_API_KEY, stt_engine=STT_ENGINE) if GEMINI_API_KEY else None

# Try to initialize Redis/RQ when queueing is enabled
redis_conn = None
rq_queue = None
if USE_QUEUE:
    try:
        from redis import Redis
        from rq import Queue
        redis_conn = Redis.from_url(REDIS_URL)
        rq_queue = Queue("default", connection=redis_conn)
        logger.info("✓ Redis queue connected")
    except Exception as e:
        logger.warning(f"⚠ Could not connect to Redis at {REDIS_URL}: {e}. Falling back to background tasks.")

if REQUIRE_GEMINI and not video_processor:
    # Fail-fast: if Gemini is required, don't start the service without a configured processor.
    logger.error("✖ GEMINI_API_KEY not set and REQUIRE_GEMINI=true - service will exit. Set GEMINI_API_KEY or set REQUIRE_GEMINI=false for dev.")
    raise SystemExit("GEMINI_API_KEY is required but not set (REQUIRE_GEMINI=true). Exiting.")

# Initialize database (PostgreSQL - Neon, Railway, etc.)
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    init_database(DATABASE_URL)
    logger.info("✓ Database connected")
else:
    logger.warning("⚠ DATABASE_URL not set - using in-memory storage (not recommended for production)")

# Initialize cloud storage (S3-compatible)
STORAGE_BUCKET = os.getenv("STORAGE_BUCKET", "")
STORAGE_ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY", "")
STORAGE_SECRET_KEY = os.getenv("STORAGE_SECRET_KEY", "")
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT", None)  # For R2, Spaces, etc.
STORAGE_REGION = os.getenv("STORAGE_REGION", "auto")

if STORAGE_BUCKET and STORAGE_ACCESS_KEY and STORAGE_SECRET_KEY:
    init_storage(STORAGE_BUCKET, STORAGE_ACCESS_KEY, STORAGE_SECRET_KEY, STORAGE_ENDPOINT, STORAGE_REGION)
    logger.info("✓ Cloud storage connected")
else:
    logger.warning("⚠ Storage not configured - files will be stored locally (not recommended for production)")

# Fallback: In-memory storage (only if database not available)
users_db = {}
videos_db = {}
jobs_db = {}  # Store processing jobs

# Dev account seeding (in-memory fallback).
# If you want a quick dev user without a DB, set DEV_USER_EMAIL and DEV_USER_PASSWORD
# in backend/.env or use the defaults below. This stores a plaintext password only
# for convenience in local development and is NOT secure for production.
DEV_USER_EMAIL = os.getenv("DEV_USER_EMAIL", "dev@localhost")
DEV_USER_PASSWORD = os.getenv("DEV_USER_PASSWORD", "DevPass123!")
if not is_database_enabled():
    if DEV_USER_EMAIL not in users_db:
        users_db[DEV_USER_EMAIL] = {
            "email": DEV_USER_EMAIL,
            # store plaintext only for dev convenience; login checks this first
            "plain_password": DEV_USER_PASSWORD,
            "disabled": False
        }
        logger.info(f"Seeded in-memory dev user: {DEV_USER_EMAIL}")

# Configuration - File Size Limits by Plan
MAX_FILE_SIZE_FREE = 500 * 1024 * 1024   # 500MB for free users
MAX_FILE_SIZE_PAID = 5 * 1024 * 1024 * 1024  # 5GB for Pro/Agency users
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"]
ALLOWED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]


def get_user_max_file_size(user_email: str) -> int:
    """Get the maximum file size allowed for a user based on their subscription plan"""
    if is_database_enabled():
        db = get_db()
        try:
            user = db.query(DBUser).filter(DBUser.email == user_email).first()
            if user and hasattr(user, 'subscription_plan'):
                # Check if subscription is active (not expired)
                if user.subscription_expires is None or user.subscription_expires > datetime.utcnow():
                    if user.subscription_plan and user.subscription_plan.value in ['pro', 'agency']:
                        return MAX_FILE_SIZE_PAID
            return MAX_FILE_SIZE_FREE
        finally:
            db.close()
    else:
        # In-memory mode - check if user has a plan set
        user = users_db.get(user_email, {})
        plan = user.get('subscription_plan', 'free')
        if plan in ['pro', 'agency']:
            return MAX_FILE_SIZE_PAID
        return MAX_FILE_SIZE_FREE

# Models
class UserCreate(BaseModel):
    email: EmailStr
    
    @validator('email')
    def email_must_be_valid(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()

class User(BaseModel):
    email: EmailStr
    disabled: Optional[bool] = False

class Token(BaseModel):
    access_token: str
    token_type: str

class VideoProcessRequest(BaseModel):
    video_source: str  # "upload", "youtube", "url", "kick"
    video_id: Optional[int] = None
    video_url: Optional[str] = None
    # Optional cookies file contents (Netscape cookies.txt format) to use when
    # downloading protected content (e.g. kick.com). Provide as a raw string.
    download_cookies: Optional[str] = None
    # Optional extra headers to pass to the downloader (e.g. {'Cookie': 'k=v'}).
    download_headers: Optional[dict] = None
    num_clips: int = 5
    clip_duration: int = 30
    resolution: str = "portrait"  # "portrait", "landscape", "square"
    
    @validator('video_source')
    def validate_source(cls, v):
        if v not in ['upload', 'youtube', 'url', 'kick']:
            raise ValueError('Invalid video source')
        return v
    
    @validator('num_clips')
    def validate_num_clips(cls, v):
        if v < 1 or v > 20:
            raise ValueError('Number of clips must be between 1 and 20')
        return v
    
    @validator('clip_duration')
    def validate_duration(cls, v):
        if v not in [15, 30, 45, 60]:
            raise ValueError('Clip duration must be 15, 30, 45, or 60 seconds')
        return v
    
    @validator('resolution')
    def validate_resolution(cls, v):
        if v not in ['portrait', 'landscape', 'square']:
            raise ValueError('Invalid resolution format')
        return v

class JobStatus(BaseModel):
    job_id: str
    status: str  # "queued", "processing", "completed", "failed"
    progress: Optional[int] = 0  # 0-100
    message: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

# Helper functions
def verify_password(plain_password, hashed_password):
    # bcrypt has a 72-byte input limit; truncate to avoid ValueError on long inputs.
    if plain_password is None:
        return False
    try:
        pw_bytes = str(plain_password).encode('utf-8', errors='ignore')
        if len(pw_bytes) > 72:
            pw_bytes = pw_bytes[:72]
        pw = pw_bytes.decode('utf-8', errors='ignore')
        return pwd_context.verify(pw, hashed_password)
    except Exception:
        return False

def get_password_hash(password):
    # Truncate to bcrypt 72-byte limit to avoid encoding errors across environments.
    if password is None:
        raise ValueError("Password cannot be None")
    pw_bytes = str(password).encode('utf-8', errors='ignore')
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
    pw = pw_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(pw)

# Auth functions moved to auth.py module

# Routes
@app.get("/")
async def root():
    return {"message": "Clip Generator API", "status": "running"}

@app.post("/dev/login")
async def dev_login():
    """
    Development-only login endpoint
    Creates/returns a dev user with a token
    WARNING: Only use in development!
    """
    # Check if we're in development mode
    is_dev = os.getenv("ENVIRONMENT", "development") == "development"
    
    if not is_dev:
        raise HTTPException(status_code=403, detail="Dev login only available in development mode")
    
    dev_email = "dev@clipgen.local"
    dev_password = "devpass123"
    
    # Create or get dev user
    if is_database_enabled():
        db = get_db()
        try:
            user = db.query(DBUser).filter(DBUser.email == dev_email).first()
            if not user:
                hashed_password = get_password_hash(dev_password)
                user = DBUser(email=dev_email, hashed_password=hashed_password, disabled=False)
                db.add(user)
                db.commit()
                logger.info("Created dev user")
        finally:
            db.close()
    else:
        # In-memory
        if dev_email not in users_db:
            users_db[dev_email] = {
                "email": dev_email,
                "hashed_password": get_password_hash(dev_password),
                "disabled": False
            }
    
    # Generate token
    access_token = create_access_token(data={"sub": dev_email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": dev_email,
        "message": "Dev login successful"
    }

@app.post("/dev/seed-data")
async def seed_dev_data(current_user: dict = Depends(get_current_user)):
    """
    Seed sample clips data for testing
    WARNING: Only use in development!
    """
    is_dev = os.getenv("ENVIRONMENT", "development") == "development"
    
    if not is_dev:
        raise HTTPException(status_code=403, detail="Seed data only available in development mode")
    
    if not is_database_enabled():
        raise HTTPException(status_code=501, detail="Database required for seeding")
    
    db = get_db()
    try:
        # Create a sample job
        job_id = str(uuid.uuid4())
        job = DBJob(
            job_id=job_id,
            user_email=current_user["email"],
            status="completed",
            progress=100,
            message="Sample data",
            num_clips=10,
            clip_duration=30,
            resolution="portrait",
            transcription="Sample transcription for testing"
        )
        db.add(job)
        db.commit()
        
        # Sample clips with realistic data
        sample_clips = [
            {
                "hook": "This is the craziest thing I've ever seen!",
                "text": "You won't believe what happened next. This is absolutely insane and everyone needs to see this.",
                "category": "surprising",
                "platform": "tiktok",
                "views": 125000,
                "revenue": 3.75,
                "virality_score": 9
            },
            {
                "hook": "Here's why everyone is talking about this",
                "text": "The secret that nobody wants you to know. This changes everything we thought we knew.",
                "category": "controversial",
                "platform": "youtube",
                "views": 85000,
                "revenue": 6.80,
                "virality_score": 8
            },
            {
                "hook": "Wait for it... 😂",
                "text": "The timing on this is absolutely perfect. I can't stop laughing at this moment.",
                "category": "humor",
                "platform": "instagram",
                "views": 67000,
                "revenue": 1.34,
                "virality_score": 7
            },
            {
                "hook": "This will blow your mind",
                "text": "I never knew this was possible until today. The science behind this is fascinating.",
                "category": "educational",
                "platform": "youtube",
                "views": 45000,
                "revenue": 3.60,
                "virality_score": 6
            },
            {
                "hook": "The moment that changed everything",
                "text": "This emotional moment hit different. You can see the exact second everything clicked.",
                "category": "emotional",
                "platform": "tiktok",
                "views": 92000,
                "revenue": 2.76,
                "virality_score": 8
            },
            {
                "hook": "Nobody expected this to happen",
                "text": "The plot twist of the century. This came out of nowhere and shocked everyone watching.",
                "category": "surprising",
                "platform": "instagram",
                "views": 38000,
                "revenue": 0.76,
                "virality_score": 7
            },
            {
                "hook": "Here's the truth they don't want you to know",
                "text": "Breaking down the real facts behind the controversy. This is what's really going on.",
                "category": "controversial",
                "platform": "youtube",
                "views": 156000,
                "revenue": 12.48,
                "virality_score": 9
            },
            {
                "hook": "I can't believe this actually worked",
                "text": "Testing this viral hack to see if it's real. The results are actually surprising.",
                "category": "educational",
                "platform": "tiktok",
                "views": 73000,
                "revenue": 2.19,
                "virality_score": 6
            },
            {
                "hook": "This is too funny 💀",
                "text": "The comedic timing here is absolutely perfect. Watch until the end for the best part.",
                "category": "humor",
                "platform": "instagram",
                "views": 54000,
                "revenue": 1.08,
                "virality_score": 7
            },
            {
                "hook": "The most wholesome moment ever",
                "text": "This restored my faith in humanity. Such a beautiful and touching moment captured on camera.",
                "category": "emotional",
                "platform": "youtube",
                "views": 28000,
                "revenue": 2.24,
                "virality_score": 5
            }
        ]
        
        for i, clip_data in enumerate(sample_clips):
            clip = DBClip(
                job_id=job_id,
                clip_number=i + 1,
                start_time=float(i * 30),
                end_time=float((i + 1) * 30),
                duration=30.0,
                text=clip_data["text"],
                hook=clip_data["hook"],
                reason=f"High engagement potential in {clip_data['category']} category",
                category=clip_data["category"],
                virality_score=clip_data["virality_score"],
                views=clip_data["views"],
                revenue=clip_data["revenue"],
                platform=clip_data["platform"],
                posted_at=datetime.utcnow() - timedelta(days=i),
                last_updated=datetime.utcnow()
            )
            db.add(clip)
        
        db.commit()
        
        logger.info(f"Seeded {len(sample_clips)} sample clips for dev user")
        
        return {
            "message": "Sample data created successfully",
            "clips_created": len(sample_clips),
            "job_id": job_id
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")
    finally:
        db.close()

@app.post("/users/register", response_model=User)
async def register(user: UserCreate, password: str):
    if is_database_enabled():
        # Use database
        db = get_db()
        try:
            # Check if user exists
            existing_user = db.query(DBUser).filter(DBUser.email == user.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Generate verification token
            import secrets
            verification_token = secrets.token_urlsafe(32)
            
            # Create new user with free credits
            hashed_password = get_password_hash(password)
            db_user = DBUser(
                email=user.email,
                hashed_password=hashed_password,
                disabled=False,
                credits=3,  # Free credits for new users
                email_verified=False,
                verification_token=verification_token,
                verification_token_expires=datetime.utcnow() + timedelta(hours=24)
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            # Send verification email
            try:
                from email_service import send_verification_email
                send_verification_email(db_user.email, verification_token)
            except Exception as e:
                logger.warning(f"Failed to send verification email: {e}")
            
            return User(email=db_user.email)
        finally:
            db.close()
    else:
        # Fallback to in-memory
        if user.email in users_db:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(password)
        users_db[user.email] = {
            "email": user.email,
            "hashed_password": hashed_password,
            "disabled": False,
            "credits": 999  # Unlimited for dev mode
        }
        return User(email=user.email)

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Development shortcut: if DISABLE_AUTH is set, return a dev token immediately
    if DISABLE_AUTH:
        token = create_access_token(data={"sub": DEV_USER_EMAIL})
        return {"access_token": token, "token_type": "bearer"}

    if is_database_enabled():
        # Use database
        db = get_db()
        try:
            user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
            if not user or not verify_password(form_data.password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            access_token = create_access_token(data={"sub": user.email})
            return {"access_token": access_token, "token_type": "bearer"}
        finally:
            db.close()
    else:
        # Fallback to in-memory
        user = users_db.get(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Development convenience: support a plaintext 'plain_password' for seeded dev users
        if user.get("plain_password") is not None:
            valid = (form_data.password == user.get("plain_password"))
        else:
            # Normal flow expects a hashed password
            valid = verify_password(form_data.password, user.get("hashed_password", ""))

        if not valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user["email"]})
        return {"access_token": access_token, "token_type": "bearer"}

@app.post("/videos/upload")
@limiter.limit("10/minute")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Get user's max file size based on subscription plan
        max_file_size = get_user_max_file_size(current_user["email"])
        
        # Validate file type
        if file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_VIDEO_TYPES)}"
            )
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Create uploads directory
        os.makedirs("uploads", exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        local_path = f"uploads/{unique_filename}"
        
        # Save file locally first (with size check based on user's plan)
        file_size = 0
        with open(local_path, "wb") as buffer:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > max_file_size:
                    os.remove(local_path)
                    max_size_mb = max_file_size / 1024 / 1024
                    max_size_gb = max_file_size / 1024 / 1024 / 1024
                    size_str = f"{max_size_gb:.1f}GB" if max_size_gb >= 1 else f"{max_size_mb:.0f}MB"
                    upgrade_msg = " Upgrade to Pro for 5GB uploads." if max_file_size == MAX_FILE_SIZE_FREE else ""
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {size_str}.{upgrade_msg}"
                    )
                buffer.write(chunk)
        
        # Upload to cloud storage if configured
        storage = get_storage()
        storage_key = None
        if storage and storage.enabled:
            storage_key = f"videos/{current_user['email']}/{unique_filename}"
            storage_url = storage.upload_file(local_path, storage_key)
            if storage_url:
                logger.info(f"Uploaded to cloud storage: {storage_key}")
        
        # Store video info in database or memory
        if is_database_enabled():
            db = get_db()
            try:
                db_video = DBVideo(
                    user_email=current_user["email"],
                    filename=file.filename,
                    storage_key=storage_key,
                    local_path=local_path,
                    size=file_size,
                    source_type="upload",
                    source_url=None
                )
                db.add(db_video)
                db.commit()
                db.refresh(db_video)
                video_id = db_video.id
            finally:
                db.close()
        else:
            video_id = len(videos_db) + 1
            videos_db[video_id] = {
                "id": video_id,
                "filename": file.filename,
                "path": local_path,
                "storage_key": storage_key,
                "size": file_size,
                "user": current_user["email"],
                "uploaded_at": datetime.utcnow().isoformat()
            }
        
        logger.info(f"Video uploaded: {file.filename} by {current_user['email']}")
        
        return {
            "message": "Video uploaded successfully",
            "video_id": video_id,
            "filename": file.filename,
            "size": file_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")

@app.get("/videos")
async def get_videos(current_user: dict = Depends(get_current_user)):
    try:
        user_videos = [
            v for v in videos_db.values() 
            if v["user"] == current_user["email"]
        ]
        return {"videos": user_videos}
    except Exception as e:
        logger.error(f"Error fetching videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch videos")

# Background task for video processing
async def process_video_task(job_id: str, request: VideoProcessRequest, user_email: str):
    db = get_db() if is_database_enabled() else None
    storage = get_storage()
    
    try:
        # Update job status
        if db:
            job = db.query(DBJob).filter(DBJob.job_id == job_id).first()
            if job:
                job.status = "processing"
                job.progress = 10
                job.message = "Preparing video..."
                db.commit()
        else:
            jobs_db[job_id]["status"] = "processing"
            jobs_db[job_id]["progress"] = 10
            jobs_db[job_id]["message"] = "Preparing video..."
            jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()
        
        if not video_processor:
            raise Exception("Video processor not initialized. Check GEMINI_API_KEY in .env file")
        
        # Get video path
        video_path = None
        if request.video_source == "upload":
            if db:
                video = db.query(DBVideo).filter(DBVideo.id == request.video_id).first()
                if not video:
                    raise Exception("Invalid video ID")
                video_path = video.local_path
            else:
                if not request.video_id or request.video_id not in videos_db:
                    raise Exception("Invalid video ID")
                video_path = videos_db[request.video_id]["path"]
        elif request.video_source == "youtube":
            if db:
                job.progress = 20
                job.message = "Downloading from YouTube..."
                db.commit()
            else:
                jobs_db[job_id]["progress"] = 20
                jobs_db[job_id]["message"] = "Downloading from YouTube..."
            video_path = video_processor.download_youtube_video(request.video_url)
        elif request.video_source == "kick":
            if db:
                job.progress = 20
                job.message = "Downloading from Kick..."
                db.commit()
            else:
                jobs_db[job_id]["progress"] = 20
                jobs_db[job_id]["message"] = "Downloading from Kick..."
            # Use the generic URL downloader which will use yt-dlp when available
            video_path = video_processor.download_video_from_url(
                request.video_url,
                cookies_text=getattr(request, 'download_cookies', None),
                extra_headers=getattr(request, 'download_headers', None)
            )
        elif request.video_source == "url":
            if db:
                job.progress = 20
                job.message = "Downloading video..."
                db.commit()
            else:
                jobs_db[job_id]["progress"] = 20
                jobs_db[job_id]["message"] = "Downloading video..."
            video_path = video_processor.download_video_from_url(
                request.video_url,
                cookies_text=getattr(request, 'download_cookies', None),
                extra_headers=getattr(request, 'download_headers', None)
            )
        
        if not video_path or not os.path.exists(video_path):
            raise Exception("Video file not found")
        
        # Process video with progress callback
        def update_progress(message, progress):
            if db:
                job.progress = progress
                job.message = message
                db.commit()
            else:
                jobs_db[job_id]["progress"] = progress
                jobs_db[job_id]["message"] = message
                jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()
            logger.info(f"Job {job_id}: {message} ({progress}%)")
        
        result = video_processor.process_video_for_clips(
            video_path=video_path,
            num_clips=request.num_clips,
            clip_duration=request.clip_duration,
            resolution=request.resolution,
            progress_callback=update_progress
        )
        
        if result["success"]:
            # Upload clips to cloud storage
            for clip_data in result["clips"]:
                clip_local_path = clip_data["path"]
                storage_key = None
                
                if storage and storage.enabled:
                    # Upload to cloud
                    storage_key = f"clips/{user_email}/{job_id}/clip_{clip_data['clip_number']}.mp4"
                    storage_url = storage.upload_file(clip_local_path, storage_key)
                    if storage_url:
                        logger.info(f"Clip {clip_data['clip_number']} uploaded to cloud: {storage_key}")
                        clip_data["storage_key"] = storage_key
                        clip_data["url"] = storage_url
                
                # Save clip to database
                if db:
                    db_clip = DBClip(
                        job_id=job_id,
                        clip_number=clip_data["clip_number"],
                        storage_key=storage_key,
                        local_path=clip_local_path,
                        start_time=clip_data["start_time"],
                        end_time=clip_data["end_time"],
                        duration=clip_data["duration"],
                        text=clip_data.get("text"),
                        hook=clip_data.get("hook"),
                        reason=clip_data.get("reason"),
                        category=clip_data.get("category"),
                        virality_score=clip_data.get("virality_score")
                    )
                    db.add(db_clip)
            # Upload captions (SRT/VTT) if present
            srt_local = result.get("srt_path")
            vtt_local = result.get("vtt_path")
            if (srt_local or vtt_local) and storage and storage.enabled:
                try:
                    if srt_local and os.path.exists(srt_local):
                        srt_key = f"captions/{user_email}/{job_id}/transcript.srt"
                        srt_url = storage.upload_file(srt_local, srt_key)
                        if srt_url:
                            result["srt_url"] = srt_url
                            logger.info(f"Uploaded SRT for job {job_id}: {srt_key}")
                    if vtt_local and os.path.exists(vtt_local):
                        vtt_key = f"captions/{user_email}/{job_id}/transcript.vtt"
                        vtt_url = storage.upload_file(vtt_local, vtt_key)
                        if vtt_url:
                            result["vtt_url"] = vtt_url
                            logger.info(f"Uploaded VTT for job {job_id}: {vtt_key}")
                except Exception as e:
                    logger.warning(f"Failed to upload captions for job {job_id}: {e}")
            
            # Update job status
            num_clips_generated = len(result.get("clips", []))
            if db:
                job.status = "completed"
                job.progress = 100
                job.message = "Processing complete!"
                job.transcription = result.get("transcription")
                job.completed_at = datetime.utcnow()
                db.commit()
            else:
                jobs_db[job_id]["status"] = "completed"
                jobs_db[job_id]["progress"] = 100
                jobs_db[job_id]["message"] = "Processing complete!"
                jobs_db[job_id]["result"] = result
                jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Job {job_id} completed successfully with {num_clips_generated} clips")
            
            # Send email notification
            try:
                from email_service import send_job_complete_email
                send_job_complete_email(user_email, job_id, num_clips_generated)
            except Exception as e:
                logger.warning(f"Failed to send job complete email: {e}")
        else:
            raise Exception(result.get("error", "Processing failed"))
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        if db:
            job.status = "failed"
            job.error = str(e)
            db.commit()
        else:
            jobs_db[job_id]["status"] = "failed"
            jobs_db[job_id]["error"] = str(e)
            jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()
    finally:
        if db:
            db.close()


def process_video_task_sync(job_id: str, request_payload: dict, user_email: str):
    """
    Synchronous wrapper to allow enqueuing the async `process_video_task` with RQ.
    Accepts a serializable dict for the request and runs the async task in an event loop.
    """
    import asyncio
    try:
        # Recreate Pydantic model if needed
        if isinstance(request_payload, dict):
            req = VideoProcessRequest(**request_payload)
        else:
            req = request_payload

        asyncio.run(process_video_task(job_id, req, user_email))
    except Exception as e:
        # RQ will capture exceptions; log here as well
        logger = logging.getLogger(__name__)
        logger.error(f"Synchronous task wrapper failed for job {job_id}: {e}")
        raise

@app.post("/videos/process")
@limiter.limit("5/minute")
async def process_video(
    request: Request,
    process_request: VideoProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Service-level check: if Gemini processor is required but not configured, return 503
        if REQUIRE_GEMINI and not video_processor:
            raise HTTPException(status_code=503, detail="Video processing backend unavailable: GEMINI_API_KEY not configured")

        # Check credits (skip in dev mode)
        if is_database_enabled():
            db = get_db()
            try:
                user = db.query(DBUser).filter(DBUser.email == current_user["email"]).first()
                if user:
                    if (user.credits or 0) < 1:
                        raise HTTPException(
                            status_code=402,
                            detail="Insufficient credits. Please purchase more credits to continue."
                        )
                    # Deduct credit
                    user.credits = (user.credits or 0) - 1
                    db.commit()
                    logger.info(f"Deducted 1 credit from {user.email}, remaining: {user.credits}")
                    
                    # Send low credits warning if needed
                    if user.credits <= 1:
                        try:
                            from email_service import send_low_credits_email
                            send_low_credits_email(user.email, user.credits)
                        except Exception as e:
                            logger.warning(f"Failed to send low credits email: {e}")
            finally:
                db.close()

        # Validate request
        if process_request.video_source == "upload" and not process_request.video_id:
            raise HTTPException(status_code=400, detail="video_id required for upload source")
        
        if process_request.video_source in ["youtube", "url", "kick"] and not process_request.video_url:
            raise HTTPException(status_code=400, detail="video_url required for this source")
        
        # Create job
        job_id = str(uuid.uuid4())
        
        if is_database_enabled():
            db = get_db()
            try:
                db_job = DBJob(
                    job_id=job_id,
                    user_email=current_user["email"],
                    video_id=process_request.video_id,
                    status="queued",
                    progress=0,
                    message="Job queued...",
                    num_clips=process_request.num_clips,
                    clip_duration=process_request.clip_duration,
                    resolution=process_request.resolution
                )
                db.add(db_job)
                db.commit()
            finally:
                db.close()
        else:
            jobs_db[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "progress": 0,
                "message": "Job queued...",
                "result": None,
                "error": None,
                "user": current_user["email"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        
        # Start processing: enqueue to Redis+RQ if enabled, otherwise use BackgroundTasks
        if USE_QUEUE and rq_queue is not None:
            try:
                from rq.job import Retry

                # enqueue the job. Pass the request as a serializable dict
                req_payload = process_request.model_dump() if hasattr(process_request, 'model_dump') else dict(process_request)
                rq_queue.enqueue(
                    process_video_task_sync,
                    job_id,
                    req_payload,
                    current_user["email"],
                    job_timeout=int(os.getenv("JOB_TIMEOUT", 3600)),
                    retry=Retry(max=2, interval=[10, 30])
                )
                logger.info(f"Job {job_id} enqueued to Redis queue")
            except Exception as e:
                logger.error(f"Failed to enqueue job to Redis queue: {e}. Falling back to BackgroundTasks.")
                background_tasks.add_task(process_video_task, job_id, process_request, current_user["email"])
        else:
            # Start background processing (local dev)
            background_tasks.add_task(process_video_task, job_id, process_request, current_user["email"])
        
        logger.info(f"Job {job_id} created for user {current_user['email']}")
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Video processing started"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start processing")

@app.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        # If using Redis queue, try to surface queue job info if available
        if USE_QUEUE and rq_queue is not None:
            try:
                from rq.registry import FailedJobRegistry
                failed_reg = FailedJobRegistry("default", connection=redis_conn)
                failed_count = len(failed_reg)
            except Exception:
                failed_count = None

        if is_database_enabled():
            db = get_db()
            try:
                job = db.query(DBJob).filter(DBJob.job_id == job_id).first()
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                # Verify ownership
                if job.user_email != current_user["email"]:
                    raise HTTPException(status_code=403, detail="Access denied")
                
                # Get clips if completed
                result = None
                if job.status == "completed":
                    clips = db.query(DBClip).filter(DBClip.job_id == job_id).all()
                    result = {
                        "clips": [
                            {
                                "clip_number": clip.clip_number,
                                "path": clip.local_path,
                                "storage_key": clip.storage_key,
                                "start_time": clip.start_time,
                                "end_time": clip.end_time,
                                "text": clip.text,
                                "hook": clip.hook,
                                "reason": clip.reason,
                                "category": clip.category,
                                "virality_score": clip.virality_score
                            }
                            for clip in clips
                        ]
                    }
                
                return JobStatus(
                    job_id=job.job_id,
                    status=job.status,
                    progress=job.progress,
                    message=job.message,
                    result=result,
                    error=job.error,
                    created_at=job.created_at.isoformat(),
                    updated_at=job.updated_at.isoformat()
                )
            finally:
                db.close()
        else:
            if job_id not in jobs_db:
                raise HTTPException(status_code=404, detail="Job not found")
            
            job = jobs_db[job_id]
            
            # Verify ownership
            if job["user"] != current_user["email"]:
                raise HTTPException(status_code=403, detail="Access denied")
            
            return JobStatus(**job)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching job status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch job status")


@app.get("/jobs/{job_id}/captions/{fmt}")
async def download_captions(
    job_id: str,
    fmt: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Serve SRT/VTT caption files for a completed job.
    If storage is configured and presigned URLs exist, redirect to them.
    Otherwise, return local file if still present in job result.
    """
    fmt = fmt.lower()
    if fmt not in ("srt", "vtt"):
        raise HTTPException(status_code=400, detail="Format must be 'srt' or 'vtt'")

    if is_database_enabled():
        db = get_db()
        try:
            job = db.query(DBJob).filter(DBJob.job_id == job_id).first()
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            if job.user_email != current_user["email"]:
                raise HTTPException(status_code=403, detail="Access denied")

            # If storage keys/URLs were saved in a JSON field or similar, prefer them
            # Here we assume captions are stored in result JSON or available via storage keys
            # Fallback: not all DB schemas include caption URLs — let the API consumer use /jobs/{job_id}
            raise HTTPException(status_code=404, detail="Captions not available via DB for this job")
        finally:
            db.close()
    else:
        # In-memory jobs_db contains job['result'] with srt_path/vtt_path OR srt_url/vtt_url
        if job_id not in jobs_db:
            raise HTTPException(status_code=404, detail="Job not found")
        job = jobs_db[job_id]
        if job["user"] != current_user["email"]:
            raise HTTPException(status_code=403, detail="Access denied")

        result = job.get("result") or {}
        # Prefer remote URL if present
        url_key = f"{fmt}_url"
        local_key = f"{fmt}_path"
        if result.get(url_key):
            # Redirect to remote URL
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=result.get(url_key))

        if result.get(local_key) and os.path.exists(result.get(local_key)):
            return FileResponse(result.get(local_key), media_type='text/vtt' if fmt == 'vtt' else 'text/plain', filename=f"transcript.{fmt}")

        raise HTTPException(status_code=404, detail="Captions not available for this job")


# Admin endpoints when queueing is enabled
@app.get("/admin/queue/status")
async def admin_queue_status():
    if not USE_QUEUE or rq_queue is None:
        raise HTTPException(status_code=404, detail="Queueing not enabled")
    try:
        from rq.registry import FailedJobRegistry
        from rq import Queue

        q = rq_queue
        stats = {
            "queue_name": q.name,
            "queued_jobs": q.count,
            "failed_jobs": len(FailedJobRegistry(q.name, connection=redis_conn)),
        }
        return stats
    except Exception as e:
        logger.error(f"Error fetching queue status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch queue status")


@app.get("/admin/queue/failed")
async def admin_failed_jobs():
    if not USE_QUEUE or rq_queue is None:
        raise HTTPException(status_code=404, detail="Queueing not enabled")
    try:
        from rq.registry import FailedJobRegistry
        from rq.job import Job

        failed_reg = FailedJobRegistry(rq_queue.name, connection=redis_conn)
        failed_ids = failed_reg.get_job_ids()
        failed_jobs = []
        for jid in failed_ids:
            try:
                job = Job.fetch(jid, connection=redis_conn)
                failed_jobs.append({
                    "id": jid,
                    "origin": job.origin,
                    "exc_info": job.exc_info,
                    "last_failed_at": str(job.enqueued_at)
                })
            except Exception:
                failed_jobs.append({"id": jid, "error": "could not fetch job"})

        return {"failed_jobs": failed_jobs}
    except Exception as e:
        logger.error(f"Error fetching failed jobs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list failed jobs")


# ============================================================================
# ADMIN DASHBOARD ENDPOINTS
# ============================================================================

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin access"""
    if not is_database_enabled():
        raise HTTPException(status_code=501, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.email == current_user["email"]).first()
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user
    finally:
        db.close()


@app.get("/admin/stats")
async def admin_stats(current_user: dict = Depends(require_admin)):
    """Get admin dashboard statistics"""
    db = get_db()
    try:
        from sqlalchemy import func
        
        # User stats
        total_users = db.query(func.count(DBUser.id)).scalar() or 0
        verified_users = db.query(func.count(DBUser.id)).filter(DBUser.email_verified == True).scalar() or 0
        
        # Job stats
        total_jobs = db.query(func.count(DBJob.id)).scalar() or 0
        completed_jobs = db.query(func.count(DBJob.id)).filter(DBJob.status == "completed").scalar() or 0
        
        # Clip stats
        total_clips = db.query(func.count(DBClip.id)).scalar() or 0
        total_revenue = db.query(func.sum(DBClip.revenue)).scalar() or 0
        
        # Payout stats
        pending_payouts = 0
        pending_payout_amount = 0.0
        if Payout:
            pending_payouts = db.query(func.count(Payout.id)).filter(Payout.status == PayoutStatus.PENDING).scalar() or 0
            pending_payout_amount = db.query(func.sum(Payout.amount)).filter(Payout.status == PayoutStatus.PENDING).scalar() or 0.0
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "total_clips": total_clips,
            "total_revenue": round(total_revenue, 2),
            "pending_payouts": pending_payouts,
            "pending_payout_amount": round(pending_payout_amount, 2)
        }
    finally:
        db.close()


@app.get("/admin/users")
async def admin_list_users(
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(require_admin)
):
    """List all users for admin"""
    db = get_db()
    try:
        users = db.query(DBUser).order_by(DBUser.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": u.id,
                "email": u.email,
                "credits": u.credits,
                "tier": u.tier.value if u.tier else "bronze",
                "email_verified": u.email_verified,
                "is_admin": u.is_admin,
                "total_clips": u.total_clips,
                "total_earnings": u.total_earnings,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    finally:
        db.close()


@app.post("/admin/users/{user_id}/add-credits")
async def admin_add_credits(
    user_id: int,
    amount: int,
    current_user: dict = Depends(require_admin)
):
    """Add credits to a user"""
    if amount <= 0 or amount > 1000:
        raise HTTPException(status_code=400, detail="Amount must be between 1 and 1000")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.credits += amount
        db.commit()
        
        return {"message": f"Added {amount} credits to {user.email}", "new_balance": user.credits}
    finally:
        db.close()


@app.post("/admin/users/{user_id}/set-subscription")
async def admin_set_subscription(
    user_id: int,
    plan: str,
    days: Optional[int] = None,
    current_user: dict = Depends(require_admin)
):
    """Set a user's subscription plan
    
    Args:
        user_id: User ID to update
        plan: 'free', 'pro', or 'agency'
        days: Number of days for subscription (None = lifetime/never expires)
    """
    from database import SubscriptionPlan
    
    if plan not in ['free', 'pro', 'agency']:
        raise HTTPException(status_code=400, detail="Plan must be 'free', 'pro', or 'agency'")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Set subscription plan
        user.subscription_plan = SubscriptionPlan(plan)
        
        # Set expiration
        if days is not None and days > 0:
            user.subscription_expires = datetime.utcnow() + timedelta(days=days)
        else:
            user.subscription_expires = None  # Never expires
        
        db.commit()
        
        expires_str = user.subscription_expires.isoformat() if user.subscription_expires else "never"
        return {
            "message": f"Updated {user.email} to {plan} plan",
            "plan": plan,
            "expires": expires_str,
            "max_file_size": "5GB" if plan in ['pro', 'agency'] else "500MB"
        }
    finally:
        db.close()


@app.get("/admin/payouts")
async def admin_list_payouts(
    limit: int = 20,
    current_user: dict = Depends(require_admin)
):
    """List payout requests"""
    if not Payout:
        return []
    
    db = get_db()
    try:
        payouts = db.query(Payout).order_by(Payout.requested_at.desc()).limit(limit).all()
        
        result = []
        for p in payouts:
            clipper = db.query(DBUser).filter(DBUser.id == p.clipper_id).first()
            result.append({
                "id": p.id,
                "clipper_id": p.clipper_id,
                "clipper_email": clipper.email if clipper else "Unknown",
                "amount": p.amount,
                "status": p.status.value if p.status else "pending",
                "requested_at": p.requested_at.isoformat() if p.requested_at else None
            })
        
        return result
    finally:
        db.close()


@app.patch("/admin/payouts/{payout_id}")
async def admin_update_payout(
    payout_id: int,
    status: str,
    current_user: dict = Depends(require_admin)
):
    """Update payout status"""
    if not Payout:
        raise HTTPException(status_code=501, detail="Payouts not configured")
    
    if status not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Status must be 'completed' or 'failed'")
    
    db = get_db()
    try:
        payout = db.query(Payout).filter(Payout.id == payout_id).first()
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        
        payout.status = PayoutStatus.COMPLETED if status == "completed" else PayoutStatus.FAILED
        payout.processed_at = datetime.utcnow()
        if status == "completed":
            payout.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": f"Payout {payout_id} marked as {status}"}
    finally:
        db.close()


@app.get("/admin/recent-activity")
async def admin_recent_activity(
    days: int = 7,
    current_user: dict = Depends(require_admin)
):
    """Get recent activity summary"""
    db = get_db()
    try:
        from sqlalchemy import func
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        new_users = db.query(func.count(DBUser.id)).filter(DBUser.created_at >= cutoff).scalar() or 0
        completed_jobs = db.query(func.count(DBJob.id)).filter(
            DBJob.status == "completed",
            DBJob.completed_at >= cutoff
        ).scalar() or 0
        new_clips = db.query(func.count(DBClip.id)).filter(DBClip.created_at >= cutoff).scalar() or 0
        
        return {
            "new_users": new_users,
            "completed_jobs": completed_jobs,
            "new_clips": new_clips,
            "period_days": days
        }
    finally:
        db.close()


@app.get("/clips/{clip_id}/download")
async def download_clip(
    clip_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        storage = get_storage()
        
        if is_database_enabled():
            db = get_db()
            try:
                # Find clip by ID
                clip = db.query(DBClip).filter(DBClip.id == clip_id).first()
                if not clip:
                    raise HTTPException(status_code=404, detail="Clip not found")
                
                # Verify ownership
                job = db.query(DBJob).filter(DBJob.job_id == clip.job_id).first()
                if not job or job.user_email != current_user["email"]:
                    raise HTTPException(status_code=403, detail="Access denied")
                
                # If clip is in cloud storage, generate presigned URL
                if clip.storage_key and storage and storage.enabled:
                    presigned_url = storage.generate_presigned_url(clip.storage_key, expiration=3600)
                    if presigned_url:
                        # Redirect to presigned URL
                        from fastapi.responses import RedirectResponse
                        return RedirectResponse(url=presigned_url)
                
                # Fallback to local file
                if clip.local_path and os.path.exists(clip.local_path):
                    return FileResponse(
                        clip.local_path,
                        media_type="video/mp4",
                        filename=f"clip_{clip.clip_number}.mp4"
                    )
                
                raise HTTPException(status_code=404, detail="Clip file not found")
            finally:
                db.close()
        else:
            # Fallback to in-memory
            clip_path = None
            for job in jobs_db.values():
                if job["user"] == current_user["email"] and job["result"]:
                    for clip_data in job["result"].get("clips", []):
                        if clip_data.get("clip_number") == clip_id:
                            clip_path = clip_data.get("path")
                            break
            
            if not clip_path or not os.path.exists(clip_path):
                raise HTTPException(status_code=404, detail="Clip not found")
            
            return FileResponse(
                clip_path,
                media_type="video/mp4",
                filename=f"clip_{clip_id}.mp4"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading clip: {str(e)}")
        raise HTTPException(status_code=500, detail="Download failed")

@app.get("/clips")
async def get_all_clips(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    current_user: dict = Depends(get_current_user)
):
    """Get all clips for current user with optional filters"""
    try:
        if not is_database_enabled():
            raise HTTPException(status_code=501, detail="Database not configured")
        
        db = get_db()
        try:
            # Get all jobs for user
            user_jobs = db.query(DBJob).filter(DBJob.user_email == current_user["email"]).all()
            job_ids = [job.job_id for job in user_jobs]
            
            # Query clips
            query = db.query(DBClip).filter(DBClip.job_id.in_(job_ids))
            
            # Apply filters
            if platform:
                query = query.filter(DBClip.platform == platform)
            if category:
                query = query.filter(DBClip.category == category)
            
            # Apply sorting
            if sort_by == "views":
                query = query.order_by(DBClip.views.desc() if order == "desc" else DBClip.views.asc())
            elif sort_by == "revenue":
                query = query.order_by(DBClip.revenue.desc() if order == "desc" else DBClip.revenue.asc())
            elif sort_by == "virality_score":
                query = query.order_by(DBClip.virality_score.desc() if order == "desc" else DBClip.virality_score.asc())
            else:  # created_at
                query = query.order_by(DBClip.created_at.desc() if order == "desc" else DBClip.created_at.asc())
            
            clips = query.all()
            
            return {
                "clips": [
                    {
                        "id": clip.id,
                        "clip_number": clip.clip_number,
                        "job_id": clip.job_id,
                        "start_time": clip.start_time,
                        "end_time": clip.end_time,
                        "duration": clip.duration,
                        "text": clip.text,
                        "hook": clip.hook,
                        "reason": clip.reason,
                        "category": clip.category,
                        "virality_score": clip.virality_score,
                        "views": clip.views,
                        "revenue": clip.revenue,
                        "platform": clip.platform,
                        "posted_at": clip.posted_at.isoformat() if clip.posted_at else None,
                        "created_at": clip.created_at.isoformat(),
                        "storage_key": clip.storage_key
                    }
                    for clip in clips
                ],
                "total": len(clips)
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clips: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch clips")

@app.get("/clips/{clip_id}")
async def get_clip_details(
    clip_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific clip"""
    try:
        if not is_database_enabled():
            raise HTTPException(status_code=501, detail="Database not configured")
        
        db = get_db()
        try:
            clip = db.query(DBClip).filter(DBClip.id == clip_id).first()
            if not clip:
                raise HTTPException(status_code=404, detail="Clip not found")
            
            # Verify ownership
            job = db.query(DBJob).filter(DBJob.job_id == clip.job_id).first()
            if not job or job.user_email != current_user["email"]:
                raise HTTPException(status_code=403, detail="Access denied")
            
            return {
                "id": clip.id,
                "clip_number": clip.clip_number,
                "job_id": clip.job_id,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "duration": clip.duration,
                "text": clip.text,
                "hook": clip.hook,
                "reason": clip.reason,
                "category": clip.category,
                "virality_score": clip.virality_score,
                "views": clip.views,
                "revenue": clip.revenue,
                "platform": clip.platform,
                "posted_at": clip.posted_at.isoformat() if clip.posted_at else None,
                "last_updated": clip.last_updated.isoformat() if clip.last_updated else None,
                "created_at": clip.created_at.isoformat(),
                "storage_key": clip.storage_key,
                "local_path": clip.local_path
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching clip details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch clip details")

class ClipAnalyticsUpdate(BaseModel):
    views: Optional[int] = None
    revenue: Optional[float] = None
    platform: Optional[str] = None
    posted_at: Optional[str] = None
    
    @validator('platform')
    def validate_platform(cls, v):
        if v and v not in ['tiktok', 'youtube', 'instagram', 'facebook', 'twitter', 'other']:
            raise ValueError('Invalid platform')
        return v

@app.put("/clips/{clip_id}/analytics")
async def update_clip_analytics(
    clip_id: int,
    analytics: ClipAnalyticsUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update analytics data for a clip"""
    try:
        if not is_database_enabled():
            raise HTTPException(status_code=501, detail="Database not configured")
        
        db = get_db()
        try:
            clip = db.query(DBClip).filter(DBClip.id == clip_id).first()
            if not clip:
                raise HTTPException(status_code=404, detail="Clip not found")
            
            # Verify ownership
            job = db.query(DBJob).filter(DBJob.job_id == clip.job_id).first()
            if not job or job.user_email != current_user["email"]:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Update fields
            if analytics.views is not None:
                clip.views = analytics.views
            if analytics.revenue is not None:
                clip.revenue = analytics.revenue
            if analytics.platform is not None:
                clip.platform = analytics.platform
            if analytics.posted_at is not None:
                clip.posted_at = datetime.fromisoformat(analytics.posted_at)
            
            clip.last_updated = datetime.utcnow()
            db.commit()
            
            logger.info(f"Updated analytics for clip {clip_id}")
            
            return {
                "message": "Analytics updated successfully",
                "clip_id": clip_id,
                "views": clip.views,
                "revenue": clip.revenue,
                "platform": clip.platform
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating clip analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update analytics")

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(current_user: dict = Depends(get_current_user)):
    """Get dashboard analytics summary"""
    try:
        if not is_database_enabled():
            raise HTTPException(status_code=501, detail="Database not configured")
        
        db = get_db()
        try:
            # Get all user's jobs
            user_jobs = db.query(DBJob).filter(DBJob.user_email == current_user["email"]).all()
            job_ids = [job.job_id for job in user_jobs]
            
            # Get all clips
            clips = db.query(DBClip).filter(DBClip.job_id.in_(job_ids)).all()
            
            # Calculate stats
            total_clips = len(clips)
            total_views = sum(clip.views for clip in clips)
            total_revenue = sum(clip.revenue for clip in clips)
            
            # Platform breakdown
            platform_stats = {}
            for clip in clips:
                if clip.platform:
                    if clip.platform not in platform_stats:
                        platform_stats[clip.platform] = {"clips": 0, "views": 0, "revenue": 0}
                    platform_stats[clip.platform]["clips"] += 1
                    platform_stats[clip.platform]["views"] += clip.views
                    platform_stats[clip.platform]["revenue"] += clip.revenue
            
            # Category breakdown
            category_stats = {}
            for clip in clips:
                if clip.category:
                    if clip.category not in category_stats:
                        category_stats[clip.category] = {"clips": 0, "views": 0, "avg_virality": 0}
                    category_stats[clip.category]["clips"] += 1
                    category_stats[clip.category]["views"] += clip.views
            
            # Calculate average virality per category
            for category in category_stats:
                category_clips = [c for c in clips if c.category == category and c.virality_score]
                if category_clips:
                    category_stats[category]["avg_virality"] = sum(c.virality_score for c in category_clips) / len(category_clips)
            
            # Top performing clips
            top_clips = sorted(clips, key=lambda x: x.views, reverse=True)[:5]
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_clips = [c for c in clips if c.created_at >= thirty_days_ago]
            
            return {
                "summary": {
                    "total_clips": total_clips,
                    "total_views": total_views,
                    "total_revenue": round(total_revenue, 2),
                    "avg_views_per_clip": round(total_views / total_clips, 2) if total_clips > 0 else 0,
                    "avg_revenue_per_clip": round(total_revenue / total_clips, 2) if total_clips > 0 else 0
                },
                "platform_stats": platform_stats,
                "category_stats": category_stats,
                "top_clips": [
                    {
                        "id": clip.id,
                        "hook": clip.hook,
                        "views": clip.views,
                        "revenue": clip.revenue,
                        "platform": clip.platform,
                        "virality_score": clip.virality_score
                    }
                    for clip in top_clips
                ],
                "recent_activity": {
                    "clips_created": len(recent_clips),
                    "views_gained": sum(c.views for c in recent_clips),
                    "revenue_earned": round(sum(c.revenue for c in recent_clips), 2)
                }
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

@app.get("/health")
async def health_check():
    storage = get_storage()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "video_processor": "ready" if video_processor else "not configured",
        "ai_model": "Gemini 2.5 Flash Lite" if video_processor else "none",
        "stt_engine": STT_ENGINE,
        "database": "connected" if is_database_enabled() else "not configured",
        "storage": "connected" if (storage and storage.enabled) else "not configured"
    }


# ============================================================================
# EMAIL VERIFICATION & PASSWORD RESET
# ============================================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str

@app.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.email == request.email).first()
        if not user:
            # Don't reveal if email exists
            return {"message": "If that email exists, a reset link has been sent"}
        
        # Generate reset token
        import secrets
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send email
        try:
            from email_service import send_password_reset_email
            send_password_reset_email(user.email, token)
        except Exception as e:
            logger.warning(f"Failed to send reset email: {e}")
        
        return {"message": "If that email exists, a reset link has been sent"}
    finally:
        db.close()


@app.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with token"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(
            DBUser.reset_token == request.token,
            DBUser.reset_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Update password
        user.hashed_password = get_password_hash(request.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        
        return {"message": "Password reset successfully"}
    finally:
        db.close()


@app.post("/auth/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """Verify email with token"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(
            DBUser.verification_token == request.token,
            DBUser.verification_token_expires > datetime.utcnow()
        ).first()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        user.email_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        db.commit()
        
        # Send welcome email
        try:
            from email_service import send_welcome_email
            send_welcome_email(user.email, user.credits or 3)
        except Exception as e:
            logger.warning(f"Failed to send welcome email: {e}")
        
        return {"message": "Email verified successfully"}
    finally:
        db.close()


@app.post("/auth/resend-verification")
async def resend_verification(current_user: dict = Depends(get_current_user)):
    """Resend verification email"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.email == current_user["email"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.email_verified:
            return {"message": "Email already verified"}
        
        # Generate new token
        import secrets
        token = secrets.token_urlsafe(32)
        user.verification_token = token
        user.verification_token_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        
        # Send email
        try:
            from email_service import send_verification_email
            send_verification_email(user.email, token)
        except Exception as e:
            logger.warning(f"Failed to send verification email: {e}")
        
        return {"message": "Verification email sent"}
    finally:
        db.close()


# ============================================================================
# CREDITS SYSTEM
# ============================================================================

@app.get("/user/credits")
async def get_user_credits(current_user: dict = Depends(get_current_user)):
    """Get current user's credit balance"""
    if not is_database_enabled():
        # In-memory mode: unlimited credits for dev
        return {"credits": 999, "is_dev_mode": True}
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.email == current_user["email"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "credits": user.credits or 0,
            "lifetime_purchased": user.lifetime_credits_purchased or 0,
            "tier": user.tier.value if user.tier else "bronze"
        }
    finally:
        db.close()


@app.get("/user/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's full profile"""
    if not is_database_enabled():
        return {
            "email": current_user["email"],
            "credits": 999,
            "email_verified": True,
            "is_dev_mode": True,
            "subscription_plan": "pro",  # Dev mode gets pro features
            "max_file_size": MAX_FILE_SIZE_PAID,
            "max_file_size_display": "5GB"
        }
    
    db = get_db()
    try:
        user = db.query(DBUser).filter(DBUser.email == current_user["email"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Determine subscription status
        subscription_plan = "free"
        if hasattr(user, 'subscription_plan') and user.subscription_plan:
            # Check if subscription is still active
            if user.subscription_expires is None or user.subscription_expires > datetime.utcnow():
                subscription_plan = user.subscription_plan.value
        
        # Get max file size for this user
        max_file_size = get_user_max_file_size(user.email)
        max_size_gb = max_file_size / 1024 / 1024 / 1024
        max_size_display = f"{max_size_gb:.1f}GB" if max_size_gb >= 1 else f"{max_file_size / 1024 / 1024:.0f}MB"
        
        return {
            "id": user.id,
            "email": user.email,
            "credits": user.credits or 0,
            "email_verified": user.email_verified or False,
            "tier": user.tier.value if user.tier else "bronze",
            "role": user.role.value if user.role else "both",
            "total_clips": user.total_clips or 0,
            "total_earnings": user.total_earnings or 0,
            "total_views": user.total_views or 0,
            "rating": user.rating or 5.0,
            "display_name": user.display_name,
            "bio": user.bio,
            "is_admin": user.is_admin or False,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "subscription_plan": subscription_plan,
            "subscription_expires": user.subscription_expires.isoformat() if hasattr(user, 'subscription_expires') and user.subscription_expires else None,
            "max_file_size": max_file_size,
            "max_file_size_display": max_size_display
        }
    finally:
        db.close()


@app.get("/user/limits")
async def get_user_limits(current_user: dict = Depends(get_current_user)):
    """Get current user's upload limits and plan features"""
    max_file_size = get_user_max_file_size(current_user["email"])
    max_size_gb = max_file_size / 1024 / 1024 / 1024
    max_size_display = f"{max_size_gb:.1f}GB" if max_size_gb >= 1 else f"{max_file_size / 1024 / 1024:.0f}MB"
    
    is_paid = max_file_size == MAX_FILE_SIZE_PAID
    
    return {
        "max_file_size": max_file_size,
        "max_file_size_display": max_size_display,
        "is_paid_plan": is_paid,
        "features": {
            "max_clips_per_job": 20 if is_paid else 5,
            "priority_processing": is_paid,
            "hd_exports": is_paid,
            "watermark_free": is_paid,
            "url_processing_limit": "unlimited" if is_paid else "10GB/month"
        },
        "upgrade_benefits": None if is_paid else {
            "max_file_size": "5GB",
            "max_clips_per_job": 20,
            "priority_processing": True,
            "price": "$29/month"
        }
    }


# ============================================================================
# PRICING INFO (for frontend)
# ============================================================================

@app.get("/pricing")
async def get_pricing():
    """Get pricing information for credits"""
    return {
        "credit_cost_per_video": 1,
        "free_credits_on_signup": 3,
        "packages": [
            {"credits": 10, "price": 9.99, "per_credit": 1.00, "popular": False},
            {"credits": 25, "price": 19.99, "per_credit": 0.80, "popular": True},
            {"credits": 50, "price": 34.99, "per_credit": 0.70, "popular": False},
            {"credits": 100, "price": 59.99, "per_credit": 0.60, "popular": False},
        ],
        "note": "Each credit = 1 video processed (up to 10 clips)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# CLIP DOWNLOAD ENDPOINT
# ============================================================================

@app.get("/clips/{clip_id}/download")
async def download_clip(
    clip_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Download a generated clip file"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Get clip from database
        clip = db.query(DBClip).filter(DBClip.id == clip_id).first()
        if not clip:
            raise HTTPException(status_code=404, detail="Clip not found")
        
        # Get file path (prefer local, fallback to storage)
        file_path = clip.local_path
        
        if not file_path or not os.path.exists(file_path):
            # Try storage key
            if clip.storage_key:
                storage = get_storage()
                if storage and storage.enabled:
                    # Generate presigned URL for cloud storage
                    try:
                        url = storage.generate_presigned_url(clip.storage_key, expiration=3600)
                        from fastapi.responses import RedirectResponse
                        return RedirectResponse(url=url)
                    except Exception as e:
                        logger.error(f"Failed to generate presigned URL: {e}")
            
            raise HTTPException(status_code=404, detail="Clip file not found")
        
        # Return local file
        return FileResponse(
            file_path,
            media_type="video/mp4",
            filename=f"clip_{clip_id}.mp4"
        )
        
    finally:
        db.close()
