@echo off
echo ========================================
echo   Production Configuration Test
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

if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it.
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python test_production_config.py

pause
