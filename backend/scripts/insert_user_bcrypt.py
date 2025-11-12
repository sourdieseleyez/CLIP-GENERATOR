#!/usr/bin/env python3
"""
Insert a dev user directly into the SQL database using bcrypt for hashing.

Usage:
  python insert_user_bcrypt.py --email dev@localhost --password DevPass123!

This script bypasses passlib to avoid environment-specific bcrypt/backends issues.
"""
import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / '.env')

def clean(s: str) -> str:
    return (s or '').strip().strip('"').strip("'")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', '-e', default='dev@localhost')
    parser.add_argument('--password', '-p', default='DevPass123!')
    args = parser.parse_args()

    database_url = clean(os.getenv('DATABASE_URL', ''))
    if not database_url:
        print('No DATABASE_URL configured in backend/.env')
        sys.exit(1)

    try:
        import database
    except Exception as e:
        print('Failed to import database module:', e)
        sys.exit(1)

    ok = database.init_database(database_url)
    if not ok:
        print('database.init_database() returned False')
        sys.exit(1)

    try:
        import bcrypt
    except Exception as e:
        print('bcrypt import failed:', e)
        sys.exit(1)

    db = database.get_db()
    try:
        existing = db.query(database.User).filter(database.User.email == args.email).first()
        if existing:
            print(f"User {args.email} already exists (id={existing.id})")
            return

        # bcrypt hash
        hashed = bcrypt.hashpw(args.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = database.User(email=args.email, hashed_password=hashed, disabled=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user {args.email} with id={user.id}")
    except Exception as e:
        print('Error inserting user:', e)
        try:
            db.rollback()
        except Exception:
            pass
    finally:
        db.close()

if __name__ == '__main__':
    main()
