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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Gemini API Key (using Flash Lite - 133x cheaper than GPT-4!)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize video processor with Gemini 2.5 Flash Lite
video_processor = GeminiVideoProcessor(GEMINI_API_KEY) if GEMINI_API_KEY else None

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
    video_source: str  # "upload", "youtube", "url"
    video_id: Optional[int] = None
    video_url: Optional[str] = None
    num_clips: int = 5
    clip_duration: int = 30
    resolution: str = "portrait"  # "portrait", "landscape", "square"
    
    @validator('video_source')
    def validate_source(cls, v):
        if v not in ['upload', 'youtube', 'url']:
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
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        if not user or not verify_password(form_data.password, user["hashed_password"]):
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
        elif request.video_source == "url":
            if db:
                job.progress = 20
                job.message = "Downloading video..."
                db.commit()
            else:
                jobs_db[job_id]["progress"] = 20
                jobs_db[job_id]["message"] = "Downloading video..."
            video_path = video_processor.download_video_from_url(request.video_url)
        
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

@app.post("/videos/process")
@limiter.limit("5/minute")
async def process_video(
    request: Request,
    process_request: VideoProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validate request
        if process_request.video_source == "upload" and not process_request.video_id:
            raise HTTPException(status_code=400, detail="video_id required for upload source")
        
        if process_request.video_source in ["youtube", "url"] and not process_request.video_url:
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
        
        # Start background processing
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

@app.get("/health")
async def health_check():
    storage = get_storage()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "video_processor": "ready" if video_processor else "not configured",
        "ai_model": "Gemini 2.5 Flash Lite" if video_processor else "none",
        "whisper_model": "OpenAI Whisper (base)",
        "database": "connected" if is_database_enabled() else "not configured",
        "storage": "connected" if (storage and storage.enabled) else "not configured"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
