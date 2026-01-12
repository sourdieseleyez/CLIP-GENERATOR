@echo off
REM Test deployed Clip Generator app

echo ========================================
echo Clip Generator - Deployment Test
echo ========================================
echo.

set /p appurl="Enter your app URL (e.g., https://clip-generator.fly.dev): "

if "%appurl%"=="" (
    echo ERROR: App URL required
    pause
    exit /b 1
)

echo.
echo Testing deployment at: %appurl%
echo.

echo [1/4] Testing health endpoint...
curl -s "%appurl%/health" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Health check passed
) else (
    echo ✗ Health check failed
)

echo.
echo [2/4] Testing API root...
curl -s "%appurl%/api/health" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ API endpoint accessible
) else (
    echo ✗ API endpoint failed
)

echo.
echo [3/4] Testing frontend...
curl -s "%appurl%/" > nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Frontend accessible
) else (
    echo ✗ Frontend failed
)

echo.
echo [4/4] Opening app in browser...
start "" "%appurl%"

echo.
echo ========================================
echo Test Complete
echo ========================================
echo.
echo If the app opened in your browser, try:
echo   1. Logging in (or using dev mode)
echo   2. Uploading a test video
echo   3. Processing a clip
echo.
echo Check logs with: fly logs
echo.
pause
