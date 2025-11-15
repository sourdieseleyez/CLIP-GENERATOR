@echo off
echo ========================================
echo   CLIP GENERATOR - DEV MODE
echo ========================================
echo.
echo Starting backend and frontend...
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:5173
echo.
echo Press Ctrl+C to stop both servers
echo.
echo ========================================
echo.

start "Backend Server" cmd /k "cd backend && python main.py"
timeout /t 3 /nobreak >nul
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting in separate windows...
echo.
echo Next steps:
echo 1. Wait for both servers to start
echo 2. Open http://localhost:5173 in your browser
echo 3. Click "Dev Login" (purple button)
echo 4. Click "Seed Sample Data" (purple button)
echo 5. Explore Dashboard and Clips Library!
echo.
pause
