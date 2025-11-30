"""
Setup script for Clip Generator Backend
Run: python setup.py
"""
import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("Clip Generator Backend Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"\nPython version: {sys.version}")
    
    if sys.version_info < (3, 9):
        print("ERROR: Python 3.9+ is required")
        sys.exit(1)
    
    # Create virtual environment if it doesn't exist
    venv_path = os.path.join(os.path.dirname(__file__), ".venv")
    
    if not os.path.exists(venv_path):
        print("\nCreating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print("  ✓ Virtual environment created")
    else:
        print("\n✓ Virtual environment exists")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Install requirements
    print("\nInstalling dependencies (this may take a few minutes)...")
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    try:
        subprocess.run([pip_path, "install", "-r", req_file], check=True)
        print("  ✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install dependencies: {e}")
        print("\nTry manually:")
        print(f"  {pip_path} install -r requirements.txt")
        sys.exit(1)
    
    # Create .env if it doesn't exist
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    env_example = os.path.join(os.path.dirname(__file__), ".env.example")
    
    if not os.path.exists(env_file) and os.path.exists(env_example):
        print("\nCreating .env from .env.example...")
        import shutil
        shutil.copy(env_example, env_file)
        print("  ✓ .env created (edit with your API keys)")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit backend/.env with your API keys:")
    print("   - GEMINI_API_KEY (required for video processing)")
    print("   - DATABASE_URL (optional, for persistence)")
    print("")
    print("2. Start the backend:")
    if sys.platform == "win32":
        print(f"   {python_path} -m uvicorn main:app --reload --port 8000")
    else:
        print(f"   {python_path} -m uvicorn main:app --reload --port 8000")
    print("")
    print("3. Or use the batch file:")
    print("   start-backend.bat")
    print("")
    print("API will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
