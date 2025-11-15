from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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
from gemini_processor import GeminiVideoProcessor
from storage import init_storage, get_storage
from database import init_database, get_db, is_database_enabled, User as DBUser, Video as DBVideo, Job as DBJob, Clip as DBClip
import logging

# Optional queueing imports will be attempted later (lazy)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Clip Generator API",
    description="AI-powered video clip generation API",
    version="1.0.0"
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
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

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# Option to disable auth for local testing (set to 'true' in backend/.env)
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "true").lower() in ("1", "true", "yes")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# Configuration
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/x-matroska"]
ALLOWED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]

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

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # If auth is disabled for local testing, return a dev user immediately
    if DISABLE_AUTH:
        return {"email": DEV_USER_EMAIL, "disabled": False}

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    if is_database_enabled():
        # Use database
        db = get_db()
        try:
            user = db.query(DBUser).filter(DBUser.email == email).first()
            if user is None:
                raise credentials_exception
            return {"email": user.email, "hashed_password": user.hashed_password, "disabled": user.disabled}
        finally:
            db.close()
    else:
        # Fallback to in-memory
        user = users_db.get(email)
        if user is None:
            raise credentials_exception
        return user

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
            
            # Create new user
            hashed_password = get_password_hash(password)
            db_user = DBUser(email=user.email, hashed_password=hashed_password, disabled=False)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
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
            "disabled": False
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
        
        # Save file locally first (with size check)
        file_size = 0
        with open(local_path, "wb") as buffer:
            while chunk := await file.read(8192):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE:
                    os.remove(local_path)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
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
            
            logger.info(f"Job {job_id} completed successfully")
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

@app.get("/clips/{clip_id}/download")
async def download_clip(
    clip_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        storage = get_storage()
        
        if is_database_enabled():
            db = get_db()
            try:
                # Find clip by ID
                clip = db.query(DBClip).filter(DBClip.id == int(clip_id)).first()
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
                    for clip in job["result"].get("clips", []):
                        if str(clip.get("clip_number")) == clip_id:
                            clip_path = clip.get("path")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
