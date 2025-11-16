"""
YouTube upload and tracking integration
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/youtube", tags=["youtube"])

# Try to import Google API client
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import pickle
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("YouTube API not available. Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 
          'https://www.googleapis.com/auth/youtube.readonly']

# Models
class YouTubeUploadRequest(BaseModel):
    clip_id: int
    job_id: int
    title: str
    description: str
    tags: List[str] = []
    category_id: str = "22"  # People & Blogs
    privacy_status: str = "public"  # public, private, unlisted


class YouTubeVideoStats(BaseModel):
    video_id: str
    views: int
    likes: int
    comments: int
    updated_at: datetime


def get_youtube_service():
    """Get authenticated YouTube service"""
    if not YOUTUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="YouTube API not configured")
    
    creds = None
    token_path = 'youtube_token.pickle'
    
    # Load saved credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need to run OAuth flow
            raise HTTPException(
                status_code=401, 
                detail="YouTube not authenticated. Run setup script first."
            )
        
        # Save credentials
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)


@router.post("/upload")
async def upload_to_youtube(
    request: YouTubeUploadRequest,
    current_user: dict = Depends(lambda: {"id": 1})  # TODO: Use real auth
):
    """Upload clip to YouTube with tracking"""
    if not YOUTUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="YouTube API not available")
    
    try:
        from database import get_db, Clip, MarketplaceJob
        
        db = get_db()
        try:
            # Get clip file
            clip = db.query(Clip).filter(Clip.id == request.clip_id).first()
            if not clip:
                raise HTTPException(status_code=404, detail="Clip not found")
            
            video_file = clip.local_path or clip.storage_key
            if not video_file or not os.path.exists(video_file):
                raise HTTPException(status_code=404, detail="Clip file not found")
            
            # Generate tracking code
            tracking_code = f"CLIP-{request.job_id}-{uuid.uuid4().hex[:8]}"
            
            # Add tracking to description
            tracked_description = f"{request.description}\n\n🔗 Tracking: {tracking_code}"
            
            # Upload to YouTube
            youtube = get_youtube_service()
            
            body = {
                'snippet': {
                    'title': request.title[:100],  # YouTube limit
                    'description': tracked_description[:5000],  # YouTube limit
                    'tags': request.tags[:500],  # YouTube limit
                    'categoryId': request.category_id
                },
                'status': {
                    'privacyStatus': request.privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
            
            request_obj = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request_obj.next_chunk()
                if status:
                    logger.info(f"Upload progress: {int(status.progress() * 100)}%")
            
            video_id = response['id']
            youtube_url = f"https://youtube.com/watch?v={video_id}"
            
            # Update job with YouTube info
            job = db.query(MarketplaceJob).filter(MarketplaceJob.id == request.job_id).first()
            if job:
                job.youtube_video_id = video_id
                job.youtube_url = youtube_url
                job.tracking_code = tracking_code
                db.commit()
            
            # Update clip with YouTube info
            clip.platform = 'youtube'
            clip.posted_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Uploaded to YouTube: {video_id}")
            
            return {
                "success": True,
                "video_id": video_id,
                "youtube_url": youtube_url,
                "tracking_code": tracking_code
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{video_id}")
async def get_video_stats(video_id: str):
    """Get YouTube video statistics"""
    if not YOUTUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="YouTube API not available")
    
    try:
        youtube = get_youtube_service()
        
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()
        
        if not response['items']:
            raise HTTPException(status_code=404, detail="Video not found")
        
        stats = response['items'][0]['statistics']
        
        return {
            "video_id": video_id,
            "views": int(stats.get('viewCount', 0)),
            "likes": int(stats.get('likeCount', 0)),
            "comments": int(stats.get('commentCount', 0)),
            "updated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-views")
async def sync_all_views():
    """Sync view counts for all tracked videos (run daily via cron)"""
    if not YOUTUBE_AVAILABLE:
        raise HTTPException(status_code=503, detail="YouTube API not available")
    
    try:
        from database import get_db, MarketplaceJob, Clip
        
        db = get_db()
        try:
            # Get all jobs with YouTube videos
            jobs = db.query(MarketplaceJob).filter(
                MarketplaceJob.youtube_video_id.isnot(None)
            ).all()
            
            youtube = get_youtube_service()
            updated_count = 0
            
            for job in jobs:
                try:
                    # Get video stats
                    request = youtube.videos().list(
                        part='statistics',
                        id=job.youtube_video_id
                    )
                    response = request.execute()
                    
                    if response['items']:
                        stats = response['items'][0]['statistics']
                        views = int(stats.get('viewCount', 0))
                        
                        # Update clip views
                        if job.clip_id:
                            clip = db.query(Clip).filter(Clip.id == job.clip_id).first()
                            if clip:
                                clip.views = views
                                clip.last_updated = datetime.utcnow()
                                
                                # Calculate revenue (example: $0.01 per view)
                                clip.revenue = views * 0.01
                                
                                updated_count += 1
                        
                        db.commit()
                        
                except Exception as e:
                    logger.error(f"Failed to sync job {job.id}: {e}")
                    continue
            
            return {
                "success": True,
                "updated_count": updated_count,
                "total_jobs": len(jobs)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"View sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/setup")
async def setup_youtube_auth():
    """Setup YouTube OAuth (run once)"""
    if not YOUTUBE_AVAILABLE:
        return {"error": "YouTube API not available"}
    
    return {
        "message": "Run this command to authenticate:",
        "command": "python -m backend.youtube_setup"
    }
