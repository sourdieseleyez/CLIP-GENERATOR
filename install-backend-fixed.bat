@echo off
echo ========================================
echo   Installing Backend (Without Database)
echo ========================================
echo.
echo Database packages are optional for testing!
echo You can add them later when needed.
echo.
cd backend
pip install -r requirements.txt
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: npm run dev
echo 2. Open: http://localhost:5173
echo 3. Click "Dev Login"
echo 4. Generate clips!
echo.
echo Note: Without database, clips are stored in memory
echo (lost when server restarts, but fine for testing)
echo.
pause
