@echo off
echo Starting Clip Generator Development Environment...
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd backend && python main.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo Development servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to stop all servers...
pause > nul

taskkill /FI "WindowTitle eq Backend*" /T /F
taskkill /FI "WindowTitle eq Frontend*" /T /F
