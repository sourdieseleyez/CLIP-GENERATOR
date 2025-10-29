@echo off
echo ========================================
echo   Clip Generator - Backend Setup
echo   Using Gemini 2.5 Flash Lite
echo ========================================
echo.

cd backend

echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo.

echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

echo [3/4] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.

echo [4/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo.
    echo ========================================
    echo   IMPORTANT: Configure your .env file!
    echo ========================================
    echo.
    echo Please edit backend\.env and add:
    echo   1. SECRET_KEY - Generate a secure random key
    echo   2. GEMINI_API_KEY - Get from https://aistudio.google.com/app/apikey
    echo.
    echo Gemini 2.5 Flash Lite is 133x cheaper than GPT-4!
    echo Cost: $0.0375 per 1M tokens
    echo.
) else (
    echo .env file already exists.
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit backend\.env with your API keys
echo   2. Run: test-backend.bat
echo.
pause
