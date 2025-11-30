"""
Admin API endpoints for managing users, payouts, and system
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database import (
    get_db, is_database_enabled,
    User, UserTier,
    Payout, PayoutStatus,
    Job, Clip, Campaign, MarketplaceJob
)
from auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# ADMIN CHECK
# ============================================================================

async def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin access"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# ============================================================================
# MODELS
# ============================================================================

class UserUpdate(BaseModel):
    credits: Optional[int] = None
    tier: Optional[str] = None
    is_admin: Optional[bool] = None
    disabled: Optional[bool] = None


class PayoutUpdate(BaseModel):
    status: str  # pending, processing, completed, failed


class StatsResponse(BaseModel):
    total_users: int
    verified_users: int
    total_jobs: int
    completed_jobs: int
    total_clips: int
    total_revenue: float
    pending_payouts: int
    pending_payout_amount: float


# ============================================================================
# DASHBOARD STATS
# ============================================================================

@router.get("/stats", response_model=StatsResponse)
async def get_admin_stats(admin: dict = Depends(require_admin)):
    """Get admin dashboard statistics"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        total_users = db.query(User).count()
        verified_users = db.query(User).filter(User.email_verified == True).count()
        total_jobs = db.query(Job).count()
        completed_jobs = db.query(Job).filter(Job.status == "completed").count()
        total_clips = db.query(Clip).count()
        
        # Calculate total revenue from clips
        clips_revenue = db.query(Clip).all()
        total_revenue = sum(c.revenue or 0 for c in clips_revenue)
        
        # Pending payouts
        pending_payouts = db.query(Payout).filter(Payout.status == PayoutStatus.PENDING).all()
        pending_count = len(pending_payouts)
        pending_amount = sum(p.amount for p in pending_payouts)
        
        return StatsResponse(
            total_users=total_users,
            verified_users=verified_users,
            total_jobs=total_jobs,
            completed_jobs=completed_jobs,
            total_clips=total_clips,
            total_revenue=total_revenue,
            pending_payouts=pending_count,
            pending_payout_amount=pending_amount
        )
    finally:
        db.close()


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users")
async def list_users(
    admin: dict = Depends(require_admin),
    limit: int = Query(50, le=200),
    offset: int = 0,
    search: Optional[str] = None
):
    """List all users with optional search"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        query = db.query(User)
        
        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        
        users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": u.id,
                "email": u.email,
                "credits": u.credits,
                "tier": u.tier.value if u.tier else "bronze",
                "is_admin": u.is_admin,
                "email_verified": u.email_verified,
                "disabled": u.disabled,
                "total_clips": u.total_clips,
                "total_earnings": u.total_earnings,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]
    finally:
        db.close()


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    update: UserUpdate,
    admin: dict = Depends(require_admin)
):
    """Update user (credits, tier, admin status, etc.)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if update.credits is not None:
            user.credits = update.credits
        
        if update.tier is not None:
            try:
                user.tier = UserTier[update.tier.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="Invalid tier")
        
        if update.is_admin is not None:
            user.is_admin = update.is_admin
        
        if update.disabled is not None:
            user.disabled = update.disabled
        
        db.commit()
        
        return {
            "message": "User updated",
            "user_id": user_id,
            "credits": user.credits,
            "tier": user.tier.value,
            "is_admin": user.is_admin,
            "disabled": user.disabled
        }
    finally:
        db.close()


@router.post("/users/{user_id}/add-credits")
async def add_credits(
    user_id: int,
    amount: int = Query(..., gt=0),
    admin: dict = Depends(require_admin)
):
    """Add credits to a user (for manual top-ups or gifts)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.credits = (user.credits or 0) + amount
        db.commit()
        
        logger.info(f"Admin added {amount} credits to user {user.email}")
        
        return {
            "message": f"Added {amount} credits",
            "user_id": user_id,
            "new_balance": user.credits
        }
    finally:
        db.close()


# ============================================================================
# PAYOUT MANAGEMENT
# ============================================================================

@router.get("/payouts")
async def list_payouts(
    admin: dict = Depends(require_admin),
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0
):
    """List all payouts"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        query = db.query(Payout)
        
        if status:
            try:
                query = query.filter(Payout.status == PayoutStatus[status.upper()])
            except KeyError:
                raise HTTPException(status_code=400, detail="Invalid status")
        
        payouts = query.order_by(Payout.requested_at.desc()).offset(offset).limit(limit).all()
        
        result = []
        for p in payouts:
            # Get user email
            user = db.query(User).filter(User.id == p.clipper_id).first()
            result.append({
                "id": p.id,
                "clipper_id": p.clipper_id,
                "clipper_email": user.email if user else "Unknown",
                "amount": p.amount,
                "status": p.status.value,
                "requested_at": p.requested_at.isoformat() if p.requested_at else None,
                "completed_at": p.completed_at.isoformat() if p.completed_at else None
            })
        
        return result
    finally:
        db.close()


@router.patch("/payouts/{payout_id}")
async def update_payout(
    payout_id: int,
    update: PayoutUpdate,
    admin: dict = Depends(require_admin)
):
    """Update payout status (approve, complete, reject)"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        payout = db.query(Payout).filter(Payout.id == payout_id).first()
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        
        try:
            new_status = PayoutStatus[update.status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        payout.status = new_status
        
        if new_status == PayoutStatus.PROCESSING:
            payout.processed_at = datetime.utcnow()
        elif new_status == PayoutStatus.COMPLETED:
            payout.completed_at = datetime.utcnow()
            
            # Send notification email
            user = db.query(User).filter(User.id == payout.clipper_id).first()
            if user:
                try:
                    from email_service import send_payout_ready_email
                    send_payout_ready_email(user.email, payout.amount, payout.id)
                except Exception as e:
                    logger.warning(f"Failed to send payout email: {e}")
        
        db.commit()
        
        return {
            "message": "Payout updated",
            "payout_id": payout_id,
            "status": payout.status.value
        }
    finally:
        db.close()


# ============================================================================
# JOBS & CLIPS
# ============================================================================

@router.get("/jobs")
async def list_jobs(
    admin: dict = Depends(require_admin),
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0
):
    """List all processing jobs"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        query = db.query(Job)
        
        if status:
            query = query.filter(Job.status == status)
        
        jobs = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": j.id,
                "job_id": j.job_id,
                "user_email": j.user_email,
                "status": j.status,
                "progress": j.progress,
                "num_clips": j.num_clips,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "completed_at": j.completed_at.isoformat() if j.completed_at else None
            }
            for j in jobs
        ]
    finally:
        db.close()


@router.get("/recent-activity")
async def get_recent_activity(
    admin: dict = Depends(require_admin),
    days: int = Query(7, le=30)
):
    """Get recent activity summary"""
    if not is_database_enabled():
        raise HTTPException(status_code=503, detail="Database not configured")
    
    db = get_db()
    try:
        since = datetime.utcnow() - timedelta(days=days)
        
        new_users = db.query(User).filter(User.created_at >= since).count()
        new_jobs = db.query(Job).filter(Job.created_at >= since).count()
        completed_jobs = db.query(Job).filter(
            Job.created_at >= since,
            Job.status == "completed"
        ).count()
        new_clips = db.query(Clip).filter(Clip.created_at >= since).count()
        
        return {
            "period_days": days,
            "new_users": new_users,
            "new_jobs": new_jobs,
            "completed_jobs": completed_jobs,
            "new_clips": new_clips
        }
    finally:
        db.close()
