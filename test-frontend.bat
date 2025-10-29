@echo off
echo Testing Frontend Setup...
echo.

echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

echo.
echo Checking frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

echo.
echo Starting frontend server...
echo Frontend will run on http://localhost:5173
echo Press Ctrl+C to stop
echo.
npm run dev
