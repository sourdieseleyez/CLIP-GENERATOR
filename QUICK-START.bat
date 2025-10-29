@echo off
echo ========================================
echo   Clip Generator - Quick Start
echo   Gemini 2.5 Flash Lite Edition
echo ========================================
echo.

echo Checking backend setup...
if not exist backend\.env (
    echo ERROR: Backend not configured!
    echo Please run: setup-backend.bat first
    echo.
    pause
    exit /b 1
)

echo Checking frontend setup...
if not exist frontend\node_modules (
    echo ERROR: Frontend not configured!
    echo Please run: cd frontend ^&^& npm install
    echo.
    pause
    exit /b 1
)

echo.
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python main.py"

timeout /t 3 /nobreak > nul

echo Starting frontend dev server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Servers Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to open browser...
pause > nul

timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
