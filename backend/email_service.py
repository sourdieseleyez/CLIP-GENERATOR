"""
Email Service for notifications
Supports SMTP (Gmail, SendGrid, etc.) or can be extended for other providers
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "ClipGen")
APP_URL = os.getenv("APP_URL", "http://localhost:5173")

def is_email_configured() -> bool:
    """Check if email is properly configured"""
    return bool(SMTP_USER and SMTP_PASSWORD)

def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
    """Send an email"""
    if not is_email_configured():
        logger.warning(f"Email not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg["To"] = to_email
        
        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

# Email Templates

def send_verification_email(to_email: str, token: str) -> bool:
    """Send email verification link"""
    verify_url = f"{APP_URL}/verify-email?token={token}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #6366f1;">Welcome to ClipGen!</h2>
        <p>Thanks for signing up. Please verify your email address to get started.</p>
        <a href="{verify_url}" style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Verify Email
        </a>
        <p style="color: #666; font-size: 14px;">Or copy this link: {verify_url}</p>
        <p style="color: #666; font-size: 12px;">This link expires in 24 hours.</p>
    </div>
    """
    
    return send_email(to_email, "Verify your ClipGen email", html)

def send_password_reset_email(to_email: str, token: str) -> bool:
    """Send password reset link"""
    reset_url = f"{APP_URL}/reset-password?token={token}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #6366f1;">Reset Your Password</h2>
        <p>You requested a password reset. Click below to set a new password.</p>
        <a href="{reset_url}" style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Reset Password
        </a>
        <p style="color: #666; font-size: 14px;">Or copy this link: {reset_url}</p>
        <p style="color: #666; font-size: 12px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
    </div>
    """
    
    return send_email(to_email, "Reset your ClipGen password", html)

def send_job_complete_email(to_email: str, job_id: str, num_clips: int) -> bool:
    """Notify user their video processing is complete"""
    clips_url = f"{APP_URL}/library"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #6366f1;">Your Clips Are Ready! 🎬</h2>
        <p>Great news! We've finished processing your video and generated <strong>{num_clips} clips</strong>.</p>
        <a href="{clips_url}" style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            View Your Clips
        </a>
        <p style="color: #666; font-size: 14px;">Job ID: {job_id}</p>
    </div>
    """
    
    return send_email(to_email, f"Your {num_clips} clips are ready!", html)

def send_low_credits_email(to_email: str, credits_remaining: int) -> bool:
    """Warn user about low credits"""
    pricing_url = f"{APP_URL}/pricing"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #f59e0b;">Low Credits Warning ⚠️</h2>
        <p>You have <strong>{credits_remaining} credits</strong> remaining.</p>
        <p>Each video processing uses 1 credit. Top up to keep generating viral clips!</p>
        <a href="{pricing_url}" style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Get More Credits
        </a>
    </div>
    """
    
    return send_email(to_email, "Low credits - top up to keep clipping!", html)

def send_payout_ready_email(to_email: str, amount: float, payout_id: int) -> bool:
    """Notify clipper their payout is ready"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #10b981;">Payout Approved! 💰</h2>
        <p>Your payout request for <strong>${amount:.2f}</strong> has been approved.</p>
        <p>You should receive the funds within 3-5 business days.</p>
        <p style="color: #666; font-size: 14px;">Payout ID: {payout_id}</p>
    </div>
    """
    
    return send_email(to_email, f"Your ${amount:.2f} payout is on the way!", html)

def send_welcome_email(to_email: str, free_credits: int = 3) -> bool:
    """Welcome new verified user"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #6366f1;">Welcome to ClipGen! 🎉</h2>
        <p>Your email is verified and you're ready to start creating viral clips.</p>
        <p>We've given you <strong>{free_credits} free credits</strong> to get started!</p>
        <h3>Quick Start:</h3>
        <ol>
            <li>Upload a video or paste a YouTube URL</li>
            <li>Our AI finds the most viral moments</li>
            <li>Download your clips and post everywhere</li>
        </ol>
        <a href="{APP_URL}" style="display: inline-block; background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Start Creating Clips
        </a>
    </div>
    """
    
    return send_email(to_email, "Welcome to ClipGen - Your free credits are ready!", html)
