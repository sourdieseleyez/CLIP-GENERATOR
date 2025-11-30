@echo off
echo ========================================
echo   Starting Clip Generator Backend
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if venv exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    .venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo Virtual environment not found!
    echo.
    echo Run setup first:
    echo   python backend/setup.py
    echo.
    echo Or install dependencies manually:
    echo   cd backend
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
)
