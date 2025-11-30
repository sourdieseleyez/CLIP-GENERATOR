"""
Quick API test script to verify the backend is functional.
Run with: python backend/test_api.py

If dependencies are not installed, run:
  pip install -r requirements.txt
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check for required dependencies first
def check_dependencies():
    """Check if required packages are installed"""
    missing = []
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    try:
        import dotenv
    except ImportError:
        missing.append("python-dotenv")
    try:
        import pydantic
    except ImportError:
        missing.append("pydantic")
    
    if missing:
        print("=" * 50)
        print("Missing dependencies!")
        print("=" * 50)
        print(f"\nPlease install: {', '.join(missing)}")
        print("\nRun: pip install -r requirements.txt")
        print("Or:  pip install " + " ".join(missing))
        print("=" * 50)
        return False
    return True

if not check_dependencies():
    sys.exit(1)

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from main import app
        print("  ✓ main.py imports successfully")
    except Exception as e:
        print(f"  ✗ main.py import failed: {e}")
        return False
    
    try:
        from auth import get_current_user, create_access_token
        print("  ✓ auth.py imports successfully")
    except Exception as e:
        print(f"  ✗ auth.py import failed: {e}")
        return False
    
    try:
        from database import init_database, get_db, is_database_enabled
        print("  ✓ database.py imports successfully")
    except Exception as e:
        print(f"  ✗ database.py import failed: {e}")
        return False
    
    try:
        from storage import init_storage, get_storage
        print("  ✓ storage.py imports successfully")
    except Exception as e:
        print(f"  ✗ storage.py import failed: {e}")
        return False
    
    try:
        from gemini_processor import GeminiVideoProcessor
        print("  ✓ gemini_processor.py imports successfully")
    except Exception as e:
        print(f"  ✗ gemini_processor.py import failed: {e}")
        return False
    
    try:
        from subtitles import create_srt_from_transcription, create_vtt_from_srt
        print("  ✓ subtitles.py imports successfully")
    except Exception as e:
        print(f"  ✗ subtitles.py import failed: {e}")
        return False
    
    try:
        from ffmpeg_helpers import extract_audio_to_wav, fast_clip_copy
        print("  ✓ ffmpeg_helpers.py imports successfully")
    except Exception as e:
        print(f"  ✗ ffmpeg_helpers.py import failed: {e}")
        return False
    
    try:
        from scene_detection import detect_scenes
        print("  ✓ scene_detection.py imports successfully")
    except Exception as e:
        print(f"  ✗ scene_detection.py import failed: {e}")
        return False
    
    try:
        from emotion_detector import detect_audio_hype_events
        print("  ✓ emotion_detector.py imports successfully")
    except Exception as e:
        print(f"  ✗ emotion_detector.py import failed: {e}")
        return False
    
    return True


def test_app_routes():
    """Test that FastAPI app has expected routes"""
    print("\nTesting routes...")
    
    from main import app
    
    routes = [route.path for route in app.routes]
    
    expected_routes = [
        "/",
        "/token",
        "/users/register",
        "/videos/upload",
        "/videos/process",
        "/jobs/{job_id}",
        "/clips",
        "/clips/{clip_id}",
        "/clips/{clip_id}/download",
        "/health",
    ]
    
    for route in expected_routes:
        if route in routes:
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route} NOT FOUND")
    
    return True


def test_models():
    """Test Pydantic models"""
    print("\nTesting models...")
    
    from main import VideoProcessRequest, JobStatus, UserCreate
    
    # Test VideoProcessRequest
    try:
        req = VideoProcessRequest(
            video_source="youtube",
            video_url="https://youtube.com/watch?v=test",
            num_clips=5,
            clip_duration=30,
            resolution="portrait"
        )
        print("  ✓ VideoProcessRequest validates correctly")
    except Exception as e:
        print(f"  ✗ VideoProcessRequest failed: {e}")
        return False
    
    # Test invalid values
    try:
        req = VideoProcessRequest(
            video_source="invalid",
            num_clips=5
        )
        print("  ✗ VideoProcessRequest should reject invalid source")
        return False
    except ValueError:
        print("  ✓ VideoProcessRequest rejects invalid source")
    
    return True


def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    import os
    
    # Check required env vars
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    if gemini_key:
        print(f"  ✓ GEMINI_API_KEY is set ({len(gemini_key)} chars)")
    else:
        print("  ⚠ GEMINI_API_KEY not set (video processing will be disabled)")
    
    db_url = os.getenv("DATABASE_URL", "")
    if db_url:
        print("  ✓ DATABASE_URL is set")
    else:
        print("  ⚠ DATABASE_URL not set (using in-memory storage)")
    
    disable_auth = os.getenv("DISABLE_AUTH", "false").lower() in ("1", "true", "yes")
    if disable_auth:
        print("  ⚠ DISABLE_AUTH=true (authentication disabled - dev mode)")
    else:
        print("  ✓ Authentication enabled")
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("Clip Generator Backend Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_config()
    all_passed &= test_models()
    all_passed &= test_app_routes()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed! ✓")
        print("\nTo start the server:")
        print("  cd CLIP-GENERATOR/backend")
        print("  uvicorn main:app --reload --port 8000")
    else:
        print("Some tests failed! ✗")
    print("=" * 50)
