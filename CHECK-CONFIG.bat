@echo off
echo ========================================
echo   Configuration Check
echo ========================================
echo.

echo [Backend Configuration]
echo.
if exist backend\.env (
    echo ✓ .env file exists
    echo.
    echo Checking for required keys...
    findstr /C:"GEMINI_API_KEY" backend\.env > nul
    if errorlevel 1 (
        echo ✗ GEMINI_API_KEY not found in .env
    ) else (
        echo ✓ GEMINI_API_KEY configured
    )
    
    findstr /C:"SECRET_KEY" backend\.env > nul
    if errorlevel 1 (
        echo ✗ SECRET_KEY not found in .env
    ) else (
        echo ✓ SECRET_KEY configured
    )
) else (
    echo ✗ .env file missing - run setup-backend.bat
)

echo.
echo [Python Dependencies]
echo.
if exist backend\venv (
    echo ✓ Virtual environment exists
    call backend\venv\Scripts\activate.bat
    python -c "import google.generativeai; print('✓ google-generativeai installed')" 2>nul || echo ✗ google-generativeai not installed
    python -c "import whisper; print('✓ openai-whisper installed')" 2>nul || echo ✗ openai-whisper not installed
    python -c "import fastapi; print('✓ fastapi installed')" 2>nul || echo ✗ fastapi not installed
    python -c "import moviepy; print('✓ moviepy installed')" 2>nul || echo ✗ moviepy not installed
) else (
    echo ✗ Virtual environment missing - run setup-backend.bat
)

echo.
echo [Frontend Configuration]
echo.
if exist frontend\node_modules (
    echo ✓ Node modules installed
) else (
    echo ✗ Node modules missing - run: cd frontend ^&^& npm install
)

if exist frontend\src\config.js (
    echo ✓ Config file exists
) else (
    echo ✗ Config file missing
)

echo.
echo ========================================
echo   Configuration Summary
echo ========================================
echo.
echo If all checks pass, run: QUICK-START.bat
echo.
pause
