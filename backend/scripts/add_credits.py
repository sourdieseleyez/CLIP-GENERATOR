#!/usr/bin/env python3
"""
Script to add credits to a user
Usage: python scripts/add_credits.py user@email.com 10
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import init_database, get_db, is_database_enabled, User

def add_credits(email: str, amount: int):
    """Add credits to a user"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set in .env")
        return False
    
    init_database(database_url)
    
    if not is_database_enabled():
        print("ERROR: Database not connected")
        return False
    
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"ERROR: User '{email}' not found")
            return False
        
        old_credits = user.credits or 0
        user.credits = old_credits + amount
        db.commit()
        
        print(f"SUCCESS: Added {amount} credits to '{email}'")
        print(f"  Previous balance: {old_credits}")
        print(f"  New balance: {user.credits}")
        return True
    finally:
        db.close()


def check_credits(email: str):
    """Check a user's credit balance"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set in .env")
        return
    
    init_database(database_url)
    
    if not is_database_enabled():
        print("ERROR: Database not connected")
        return
    
    db = get_db()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"ERROR: User '{email}' not found")
            return
        
        print(f"User: {email}")
        print(f"  Credits: {user.credits or 0}")
        print(f"  Tier: {user.tier.value if user.tier else 'bronze'}")
        print(f"  Email verified: {user.email_verified}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/add_credits.py <email> <amount>  - Add credits to user")
        print("  python scripts/add_credits.py <email> --check   - Check user's credits")
        sys.exit(1)
    
    email = sys.argv[1]
    
    if len(sys.argv) >= 3:
        if sys.argv[2] == "--check":
            check_credits(email)
        else:
            try:
                amount = int(sys.argv[2])
                add_credits(email, amount)
            except ValueError:
                print("ERROR: Amount must be a number")
                sys.exit(1)
    else:
        check_credits(email)
