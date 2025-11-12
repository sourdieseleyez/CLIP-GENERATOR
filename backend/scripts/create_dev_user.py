#!/usr/bin/env python3
"""
Create a development user for the Clip Generator backend.

Usage:
  python create_dev_user.py --email dev@localhost --password 'DevPass123!'

If a DATABASE_URL is present in `backend/.env` this script will attempt to
connect and insert the user into the `users` table. If no database is
configured it will write a small local JSON file `backend/dev_user.json` as
a fallback (note: the running FastAPI in-memory store won't pick that up).
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Ensure backend package path is importable when running the script directly
THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv(ROOT_DIR / '.env')

from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def clean_db_url(url: str) -> str:
    if not url:
        return ""
    return url.strip().strip('"').strip("'")


def create_in_db(database_url: str, email: str, password: str) -> bool:
    try:
        import database
    except Exception as e:
        print(f"Failed to import database module: {e}")
        return False

    database_url = clean_db_url(database_url)
    ok = database.init_database(database_url)
    if not ok:
        print("Database init failed. Check DATABASE_URL in backend/.env and connectivity.")
        return False

    db = database.get_db()
    try:
        existing = db.query(database.User).filter(database.User.email == email).first()
        if existing:
            print(f"User '{email}' already exists in the database (id={existing.id}).")
            return True

        hashed = pwd_ctx.hash(password)
        user = database.User(email=email, hashed_password=hashed, disabled=False)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user '{email}' with id={user.id}.")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        try:
            db.rollback()
        except Exception:
            pass
        return False
    finally:
        db.close()


def create_local_fallback(email: str, password: str) -> bool:
    hashed = pwd_ctx.hash(password)
    out = {
        "email": email,
        "hashed_password": hashed,
        "disabled": False
    }
    out_path = ROOT_DIR / 'dev_user.json'
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2)
        print(f"No database configured. Wrote fallback dev user to: {out_path}")
        return True
    except Exception as e:
        print(f"Failed to write fallback file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', '-e', default='dev@localhost')
    parser.add_argument('--password', '-p', default='DevPass123!')
    args = parser.parse_args()

    # Prefer DATABASE_URL from environment (.env)
    database_url = os.getenv('DATABASE_URL', '').strip()

    if database_url:
        success = create_in_db(database_url, args.email, args.password)
        if not success:
            print("Falling back to local dev user file.")
            create_local_fallback(args.email, args.password)
    else:
        create_local_fallback(args.email, args.password)

    print('\nDev account details:')
    print(f"  email: {args.email}")
    print(f"  password: {args.password}")
    print('\nIf you want the API to recognize this user ensure your backend is configured to use the database in backend/.env.\n')


if __name__ == '__main__':
    main()
