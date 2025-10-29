@echo off
echo ========================================
echo   Testing Gemini 2.5 Flash Lite
echo ========================================
echo.

cd backend

if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run: setup-backend.bat first
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python test_gemini.py

pause
