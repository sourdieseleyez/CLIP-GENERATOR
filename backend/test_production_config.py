"""
Production Configuration Test
Verifies database and storage connections
"""

import os
from dotenv import load_dotenv
from database import init_database, is_database_enabled
from storage import init_storage, get_storage
import google.generativeai as genai

load_dotenv()

def test_production_config():
    print("=" * 60)
    print("  Production Configuration Test")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test 1: Gemini API
    print("[1/4] Testing Gemini API...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("  ❌ GEMINI_API_KEY not set")
        all_passed = False
    else:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content("Say 'OK'")
            print(f"  ✓ Gemini API working: {response.text[:50]}")
        except Exception as e:
            print(f"  ❌ Gemini API failed: {e}")
            all_passed = False
    print()
    
    # Test 2: Database
    print("[2/4] Testing Database...")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("  ⚠ DATABASE_URL not set (will use in-memory storage)")
        print("  ℹ For production, set up Neon: https://neon.tech")
    else:
        try:
            success = init_database(db_url)
            if success and is_database_enabled():
                print("  ✓ Database connected successfully")
            else:
                print("  ❌ Database connection failed")
                all_passed = False
        except Exception as e:
            print(f"  ❌ Database error: {e}")
            all_passed = False
    print()
    
    # Test 3: Cloud Storage
    print("[3/4] Testing Cloud Storage...")
    bucket = os.getenv("STORAGE_BUCKET")
    access_key = os.getenv("STORAGE_ACCESS_KEY")
    secret_key = os.getenv("STORAGE_SECRET_KEY")
    endpoint = os.getenv("STORAGE_ENDPOINT")
    region = os.getenv("STORAGE_REGION", "auto")
    
    if not bucket or not access_key or not secret_key:
        print("  ⚠ Storage not configured (will use local files)")
        print("  ℹ For production, set up Cloudflare R2 or AWS S3")
    else:
        try:
            storage = init_storage(bucket, access_key, secret_key, endpoint, region)
            if storage and storage.enabled:
                print(f"  ✓ Storage connected: {bucket}")
            else:
                print("  ❌ Storage connection failed")
                all_passed = False
        except Exception as e:
            print(f"  ❌ Storage error: {e}")
            all_passed = False
    print()
    
    # Test 4: Secret Key
    print("[4/4] Testing Secret Key...")
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key or secret_key == "your-secret-key-change-in-production":
        print("  ❌ SECRET_KEY not set or using default")
        print("  ℹ Generate with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        all_passed = False
    else:
        print("  ✓ SECRET_KEY configured")
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("  ✅ All Tests Passed - Ready for Production!")
    else:
        print("  ⚠ Some Tests Failed - Check Configuration")
    print("=" * 60)
    print()
    
    # Configuration Summary
    print("Configuration Summary:")
    print("-" * 60)
    print(f"  Gemini API:     {'✓ Configured' if gemini_key else '✗ Missing'}")
    print(f"  Database:       {'✓ Configured' if db_url else '⚠ Using in-memory'}")
    print(f"  Cloud Storage:  {'✓ Configured' if bucket else '⚠ Using local files'}")
    print(f"  Secret Key:     {'✓ Configured' if (secret_key and secret_key != 'your-secret-key-change-in-production') else '✗ Missing'}")
    print("-" * 60)
    print()
    
    if not all_passed:
        print("Next Steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in all required values")
        print("3. See PRODUCTION-SETUP.md for detailed instructions")
        print()
    
    return all_passed

if __name__ == "__main__":
    success = test_production_config()
    input("Press Enter to exit...")
    exit(0 if success else 1)
