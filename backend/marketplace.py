"""
Marketplace API endpoints for campaign posting and job management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

from database import (
    get_db, is_database_enabled,
    Campaign, CampaignStatus,
    MarketplaceJob, MarketplaceJobStatus,
    User, UserTier, UserRole,
    Payout, PayoutStatus
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class CampaignCreate(BaseModel):
    title: str
    description: str
    video_url: str
    num_clips_needed: int = 5
    clip_duration: int = 30
    resolution: str = "portrait"
    style_notes: Optional[str] = None
    budget_per_clip: float
    deadline: Optional[datetime] = None


class CampaignResponse(BaseModel):
    id: int
    title: str
    description: str
    video_url: str
    num_clips_needed: int
    clip_duration: int
    resolution: str
    budget_per_clip: float
    total_budget: float
    status: str
    clips_submitted: int
    clips_approved: int
    created_at: datetime
    deadline: Optional[datetime]


class JobClaimRequest(BaseModel):
    campaign_id: int


class JobSubmitRequest(BaseModel):
    job_id: int
    clip_id: int
    youtube_url: Optional[str] = None


class JobReviewRequest(BaseModel):
    job_id: int
    approved: bool
    feedback: Optional[str] = None
    rating: Optional[int] = None  # 1-5 stars


class PayoutRequest(BaseModel):
    job_ids: List[int]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_split(tier: str, amount: float) -> tuple:
    """Calculate clipper share and platform fee based on tier"""
    splits = {
        "bronze": 0.70,
        "silver": 0.75,
        "gold": 0.80,
        "platinum": 0.85
    }
    
    clipper_percentage = splits.get(tier.lower(), 0.70)
    clipper_share = amount * clipper_percentage
    platform_fee = amount - clipper_share
    
    return clipper_share, platform_fee


# Import auth from shared module (no circular import)
from auth import get_current_user


# ============================================================================
# CAMPAIGN ENDPOINTS (CLIENT SIDE)
# ============================================================================

@router.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new campaign (clients only)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Calculate total budget
        total_budget = campaign.budget_per_clip * campaign.num_clips_needed
        
        # Create campaign
        db_campaign = Campaign(
            client_id=current_user["id"],
            title=campaign.title,
            description=campaign.description,
            video_url=campaign.video_url,
            num_clips_needed=campaign.num_clips_needed,
            clip_duration=campaign.clip_duration,
            resolution=campaign.resolution,
            style_notes=campaign.style_notes,
            budget_per_clip=campaign.budget_per_clip,
            total_budget=total_budget,
            deadline=campaign.deadline,
            status=CampaignStatus.ACTIVE
        )
        
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        
        return CampaignResponse(
            id=db_campaign.id,
            title=db_campaign.title,
            description=db_campaign.description,
            video_url=db_campaign.video_url,
            num_clips_needed=db_campaign.num_clips_needed,
            clip_duration=db_campaign.clip_duration,
            resolution=db_campaign.resolution,
            budget_per_clip=db_campaign.budget_per_clip,
            total_budget=db_campaign.total_budget,
            status=db_campaign.status.value,
            clips_submitted=db_campaign.clips_submitted,
            clips_approved=db_campaign.clips_approved,
            created_at=db_campaign.created_at,
            deadline=db_campaign.deadline
        )
    finally:
        db.close()


@router.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    status: Optional[str] = "active",
    limit: int = 20
):
    """List available campaigns (public for clippers to browse)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        query = db.query(Campaign)
        
        if status:
            query = query.filter(Campaign.status == CampaignStatus[status.upper()])
        
        campaigns = query.order_by(Campaign.created_at.desc()).limit(limit).all()
        
        return [
            CampaignResponse(
                id=c.id,
                title=c.title,
                description=c.description,
                video_url=c.video_url,
                num_clips_needed=c.num_clips_needed,
                clip_duration=c.clip_duration,
                resolution=c.resolution,
                budget_per_clip=c.budget_per_clip,
                total_budget=c.total_budget,
                status=c.status.value,
                clips_submitted=c.clips_submitted,
                clips_approved=c.clips_approved,
                created_at=c.created_at,
                deadline=c.deadline
            )
            for c in campaigns
        ]
    finally:
        db.close()


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int):
    """Get campaign details"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        return CampaignResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            video_url=campaign.video_url,
            num_clips_needed=campaign.num_clips_needed,
            clip_duration=campaign.clip_duration,
            resolution=campaign.resolution,
            budget_per_clip=campaign.budget_per_clip,
            total_budget=campaign.total_budget,
            status=campaign.status.value,
            clips_submitted=campaign.clips_submitted,
            clips_approved=campaign.clips_approved,
            created_at=campaign.created_at,
            deadline=campaign.deadline
        )
    finally:
        db.close()


# ============================================================================
# JOB ENDPOINTS (CLIPPER SIDE)
# ============================================================================

@router.post("/jobs/claim")
async def claim_job(
    request: JobClaimRequest,
    current_user: dict = Depends(get_current_user)
):
    """Claim a campaign job (clippers only)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Get campaign
        campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if campaign.status != CampaignStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Campaign is not active")
        
        # Check if user already has a job for this campaign
        existing = db.query(MarketplaceJob).filter(
            MarketplaceJob.campaign_id == request.campaign_id,
            MarketplaceJob.clipper_id == current_user["id"]
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="You already claimed this campaign")
        
        # Get user tier for split calculation
        user = db.query(User).filter(User.id == current_user["id"]).first()
        tier = user.tier.value if user else "bronze"
        
        # Calculate payment split
        clipper_share, platform_fee = calculate_split(tier, campaign.budget_per_clip)
        
        # Create job
        job = MarketplaceJob(
            campaign_id=campaign.id,
            clipper_id=current_user["id"],
            agreed_price=campaign.budget_per_clip,
            clipper_share=clipper_share,
            platform_fee=platform_fee,
            status=MarketplaceJobStatus.CLAIMED
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return {
            "job_id": job.id,
            "campaign_id": campaign.id,
            "agreed_price": job.agreed_price,
            "your_earnings": job.clipper_share,
            "platform_fee": job.platform_fee,
            "status": job.status.value
        }
    finally:
        db.close()


@router.post("/jobs/submit")
async def submit_job(
    request: JobSubmitRequest,
    current_user: dict = Depends(get_current_user)
):
    """Submit completed clip for review"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Get job
        job = db.query(MarketplaceJob).filter(
            MarketplaceJob.id == request.job_id,
            MarketplaceJob.clipper_id == current_user["id"]
        ).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status not in [MarketplaceJobStatus.CLAIMED, MarketplaceJobStatus.IN_PROGRESS]:
            raise HTTPException(status_code=400, detail="Job cannot be submitted in current status")
        
        # Update job
        job.clip_id = request.clip_id
        job.youtube_url = request.youtube_url
        job.status = MarketplaceJobStatus.SUBMITTED
        job.submitted_at = datetime.utcnow()
        
        # Update campaign stats
        campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
        if campaign:
            campaign.clips_submitted += 1
        
        db.commit()
        
        return {
            "message": "Clip submitted for review",
            "job_id": job.id,
            "status": job.status.value
        }
    finally:
        db.close()


@router.get("/jobs/my-jobs")
async def get_my_jobs(
    current_user: dict = Depends(get_current_user)
):
    """Get clipper's jobs"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        jobs = db.query(MarketplaceJob).filter(
            MarketplaceJob.clipper_id == current_user["id"]
        ).order_by(MarketplaceJob.claimed_at.desc()).all()
        
        return [
            {
                "job_id": j.id,
                "campaign_id": j.campaign_id,
                "status": j.status.value,
                "agreed_price": j.agreed_price,
                "your_earnings": j.clipper_share,
                "claimed_at": j.claimed_at,
                "submitted_at": j.submitted_at,
                "approved_at": j.approved_at
            }
            for j in jobs
        ]
    finally:
        db.close()


# ============================================================================
# REVIEW ENDPOINTS (CLIENT SIDE)
# ============================================================================

@router.post("/jobs/review")
async def review_job(
    request: JobReviewRequest,
    current_user: dict = Depends(get_current_user)
):
    """Review and approve/reject submitted clip"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Get job
        job = db.query(MarketplaceJob).filter(MarketplaceJob.id == request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Verify ownership
        campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
        if campaign.client_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        if job.status != MarketplaceJobStatus.SUBMITTED:
            raise HTTPException(status_code=400, detail="Job not in submitted status")
        
        # Update job
        if request.approved:
            job.status = MarketplaceJobStatus.APPROVED
            job.approved_at = datetime.utcnow()
            campaign.clips_approved += 1
            
            # Update clipper stats
            clipper = db.query(User).filter(User.id == job.clipper_id).first()
            if clipper:
                clipper.total_clips += 1
                if request.rating:
                    # Update rating
                    total = clipper.rating * clipper.rating_count + request.rating
                    clipper.rating_count += 1
                    clipper.rating = total / clipper.rating_count
        else:
            job.status = MarketplaceJobStatus.REJECTED
        
        job.client_feedback = request.feedback
        job.client_rating = request.rating
        
        db.commit()
        
        return {
            "message": "Review submitted",
            "job_id": job.id,
            "status": job.status.value
        }
    finally:
        db.close()


# ============================================================================
# PAYOUT ENDPOINTS
# ============================================================================

@router.post("/payouts/request")
async def request_payout(
    request: PayoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Request payout for approved jobs"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Get approved jobs
        jobs = db.query(MarketplaceJob).filter(
            MarketplaceJob.id.in_(request.job_ids),
            MarketplaceJob.clipper_id == current_user["id"],
            MarketplaceJob.status == MarketplaceJobStatus.APPROVED
        ).all()
        
        if not jobs:
            raise HTTPException(status_code=400, detail="No approved jobs found")
        
        # Calculate total
        total_amount = sum(j.clipper_share for j in jobs)
        
        # Create payout
        payout = Payout(
            clipper_id=current_user["id"],
            amount=total_amount,
            job_ids=json.dumps([j.id for j in jobs]),
            status=PayoutStatus.PENDING
        )
        
        db.add(payout)
        
        # Mark jobs as paid
        for job in jobs:
            job.status = MarketplaceJobStatus.PAID
            job.paid_at = datetime.utcnow()
        
        db.commit()
        db.refresh(payout)
        
        return {
            "payout_id": payout.id,
            "amount": payout.amount,
            "job_count": len(jobs),
            "status": payout.status.value,
            "message": "Payout request submitted. You will receive payment within 3-5 business days."
        }
    finally:
        db.close()


@router.get("/payouts/my-payouts")
async def get_my_payouts(
    current_user: dict = Depends(get_current_user)
):
    """Get clipper's payout history"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        payouts = db.query(Payout).filter(
            Payout.clipper_id == current_user["id"]
        ).order_by(Payout.requested_at.desc()).all()
        
        return [
            {
                "payout_id": p.id,
                "amount": p.amount,
                "status": p.status.value,
                "requested_at": p.requested_at,
                "completed_at": p.completed_at
            }
            for p in payouts
        ]
    finally:
        db.close()


@router.post("/calculate-bonuses")
async def calculate_performance_bonuses():
    """Calculate and distribute performance bonuses based on view milestones"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        # Bonus tiers (views → bonus multiplier)
        bonus_tiers = {
            100000: 1.2,   # 100k views = 20% bonus
            500000: 1.5,   # 500k views = 50% bonus
            1000000: 2.0,  # 1M views = 100% bonus
            5000000: 3.0   # 5M views = 200% bonus
        }
        
        # Get all approved jobs with YouTube videos
        jobs = db.query(MarketplaceJob).filter(
            MarketplaceJob.status == MarketplaceJobStatus.APPROVED,
            MarketplaceJob.youtube_video_id.isnot(None)
        ).all()
        
        bonuses_paid = 0
        total_bonus_amount = 0.0
        
        for job in jobs:
            if not job.clip_id:
                continue
            
            # Get clip views
            clip = db.query(Clip).filter(Clip.id == job.clip_id).first()
            if not clip or clip.views == 0:
                continue
            
            # Calculate bonus based on highest tier reached
            bonus_multiplier = 1.0
            for threshold, multiplier in sorted(bonus_tiers.items()):
                if clip.views >= threshold:
                    bonus_multiplier = multiplier
            
            # Calculate bonus (only if multiplier > 1)
            if bonus_multiplier > 1.0:
                base_earnings = job.clipper_share
                bonus_amount = base_earnings * (bonus_multiplier - 1.0)
                
                # Only pay if not already paid
                if job.bonus_earned < bonus_amount:
                    new_bonus = bonus_amount - job.bonus_earned
                    job.bonus_earned = bonus_amount
                    job.total_views = clip.views
                    
                    # Update clipper total earnings
                    clipper = db.query(User).filter(User.id == job.clipper_id).first()
                    if clipper:
                        clipper.total_earnings += new_bonus
                        clipper.total_views = (clipper.total_views or 0) + clip.views
                    
                    bonuses_paid += 1
                    total_bonus_amount += new_bonus
        
        db.commit()
        
        return {
            "success": True,
            "bonuses_paid": bonuses_paid,
            "total_amount": total_bonus_amount,
            "message": f"Distributed ${total_bonus_amount:.2f} in bonuses to {bonuses_paid} clippers"
        }
        
    finally:
        db.close()
