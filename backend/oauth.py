"""
OAuth Authentication Module
Supports Google and GitHub OAuth for Better Auth style authentication

UPDATED January 2025:
- Google Identity Services (new Google Sign-In)
- GitHub OAuth App integration
- Secure token handling with state parameter
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
import os
import secrets
from urllib.parse import urlencode
from auth import create_access_token
from database import get_db, is_database_enabled, User as DBUser
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["OAuth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

# Frontend URL for redirects
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Store OAuth states temporarily (in production, use Redis)
oauth_states = {}


def get_or_create_oauth_user(email: str, name: str = None, provider: str = "oauth"):
    """Get existing user or create new one for OAuth login"""
    if is_database_enabled():
        db = get_db()
        try:
            user = db.query(DBUser).filter(DBUser.email == email).first()
            if not user:
                # Create new user with random password (they'll use OAuth)
                random_password = secrets.token_urlsafe(32)
                hashed_password = pwd_context.hash(random_password)
                user = DBUser(
                    email=email,
                    hashed_password=hashed_password,
                    disabled=False
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created new OAuth user: {email} via {provider}")
            return {"id": user.id, "email": user.email}
        finally:
            db.close()
    else:
        # In-memory fallback
        from main import users_db
        if email not in users_db:
            random_password = secrets.token_urlsafe(32)
            users_db[email] = {
                "email": email,
                "hashed_password": pwd_context.hash(random_password),
                "disabled": False
            }
            logger.info(f"Created new OAuth user (in-memory): {email}")
        return {"email": email}


# ============ GOOGLE OAUTH ============

@router.get("/google")
async def google_login():
    """Initiate Google OAuth flow"""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=501, detail="Google OAuth not configured")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "google"}
    
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": f"{BACKEND_URL}/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback"""
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=missing_params")
    
    # Verify state
    if state not in oauth_states:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=invalid_state")
    
    del oauth_states[state]
    
    try:
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": f"{BACKEND_URL}/auth/google/callback"
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Google token error: {token_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}?error=token_exchange_failed")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=user_info_failed")
            
            user_info = user_response.json()
            email = user_info.get("email")
            name = user_info.get("name", "")
            
            if not email:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=no_email")
            
            # Get or create user
            user = get_or_create_oauth_user(email, name, "google")
            
            # Create JWT token
            jwt_token = create_access_token(data={"sub": email})
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{FRONTEND_URL}?token={jwt_token}&email={email}"
            )
            
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=oauth_failed")


# ============ GITHUB OAUTH ============

@router.get("/github")
async def github_login():
    """Initiate GitHub OAuth flow"""
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=501, detail="GitHub OAuth not configured")
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {"provider": "github"}
    
    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": f"{BACKEND_URL}/auth/github/callback",
        "scope": "user:email",
        "state": state
    }
    
    auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
    return RedirectResponse(url=auth_url)


@router.get("/github/callback")
async def github_callback(code: str = None, state: str = None, error: str = None):
    """Handle GitHub OAuth callback"""
    if error:
        return RedirectResponse(url=f"{FRONTEND_URL}?error={error}")
    
    if not code or not state:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=missing_params")
    
    # Verify state
    if state not in oauth_states:
        return RedirectResponse(url=f"{FRONTEND_URL}?error=invalid_state")
    
    del oauth_states[state]
    
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": code
                },
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                logger.error(f"GitHub token error: {token_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}?error=token_exchange_failed")
            
            tokens = token_response.json()
            access_token = tokens.get("access_token")
            
            if not access_token:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=no_access_token")
            
            # Get user info
            user_response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            if user_response.status_code != 200:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=user_info_failed")
            
            user_info = user_response.json()
            
            # GitHub might not return email in user info, need to fetch separately
            email = user_info.get("email")
            
            if not email:
                # Fetch emails separately
                emails_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                
                if emails_response.status_code == 200:
                    emails = emails_response.json()
                    # Get primary email
                    for e in emails:
                        if e.get("primary") and e.get("verified"):
                            email = e.get("email")
                            break
                    # Fallback to first verified email
                    if not email:
                        for e in emails:
                            if e.get("verified"):
                                email = e.get("email")
                                break
            
            if not email:
                return RedirectResponse(url=f"{FRONTEND_URL}?error=no_email")
            
            name = user_info.get("name") or user_info.get("login", "")
            
            # Get or create user
            user = get_or_create_oauth_user(email, name, "github")
            
            # Create JWT token
            jwt_token = create_access_token(data={"sub": email})
            
            # Redirect to frontend with token
            return RedirectResponse(
                url=f"{FRONTEND_URL}?token={jwt_token}&email={email}"
            )
            
    except Exception as e:
        logger.error(f"GitHub OAuth error: {str(e)}")
        return RedirectResponse(url=f"{FRONTEND_URL}?error=oauth_failed")
