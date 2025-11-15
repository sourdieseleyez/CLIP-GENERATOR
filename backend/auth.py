"""
Authentication utilities - shared between main.py and marketplace.py
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "true").lower() in ("1", "true", "yes")
DEV_USER_EMAIL = os.getenv("DEV_USER_EMAIL", "dev@localhost")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from JWT token"""
    from database import get_db, is_database_enabled, User as DBUser
    
    # If auth is disabled for local testing, return a dev user immediately
    if DISABLE_AUTH:
        # For dev mode, try to get a real user or return mock
        if is_database_enabled():
            db = get_db()
            try:
                user = db.query(DBUser).filter(DBUser.email == DEV_USER_EMAIL).first()
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "disabled": user.disabled
                    }
            finally:
                db.close()
        
        # Fallback mock user for dev
        return {"id": 1, "email": DEV_USER_EMAIL, "disabled": False}

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
            return {
                "id": user.id,  # ✅ Include user ID
                "email": user.email,
                "disabled": user.disabled
            }
        finally:
            db.close()
    else:
        # Fallback to in-memory (shouldn't happen in production)
        raise HTTPException(
            status_code=503,
            detail="Database not configured"
        )


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
