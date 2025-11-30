#!/usr/bin/env python3
"""
Script to make a user an admin
Usage: python scripts/make_admin.py user@email.com
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import init_database, get_db, is_database_enabled, User

def make_admin(email: str):
    """Make a user an admin"""
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
        
        user.is_admin = True
        db.commit()
        
        print(f"SUCCESS: User '{email}' is now an admin")
        return True
    finally:
        db.close()


def list_admins():
    """List all admin users"""
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
        admins = db.query(User).filter(User.is_admin == True).all()
        if not admins:
            print("No admin users found")
        else:
            print("Admin users:")
            for admin in admins:
                print(f"  - {admin.email}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/make_admin.py <email>  - Make user an admin")
        print("  python scripts/make_admin.py --list   - List all admins")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--list":
        list_admins()
    else:
        make_admin(arg)
