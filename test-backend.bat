@echo off
echo Testing Backend Setup...
echo.

echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Checking backend dependencies...
cd backend
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting backend server...
echo Backend will run on http://localhost:8000
echo Press Ctrl+C to stop
echo.
python main.py
