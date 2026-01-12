@echo off
REM Quick deployment script for Fly.io

echo ========================================
echo Clip Generator - Fly.io Deployment
echo ========================================
echo.

cd /d "%~dp0"

:menu
echo What would you like to do?
echo.
echo 1. Deploy app
echo 2. View logs
echo 3. Check status
echo 4. Open app in browser
echo 5. Set secrets
echo 6. Create volume
echo 7. SSH into machine
echo 8. Exit
echo.
set /p choice="Enter choice (1-8): "

if "%choice%"=="1" goto deploy
if "%choice%"=="2" goto logs
if "%choice%"=="3" goto status
if "%choice%"=="4" goto open
if "%choice%"=="5" goto secrets
if "%choice%"=="6" goto volume
if "%choice%"=="7" goto ssh
if "%choice%"=="8" goto end
goto menu

:deploy
echo.
echo Deploying to Fly.io...
fly deploy
echo.
pause
goto menu

:logs
echo.
echo Viewing logs (Ctrl+C to exit)...
fly logs
echo.
pause
goto menu

:status
echo.
fly status
echo.
pause
goto menu

:open
echo.
echo Opening app in browser...
fly open
echo.
pause
goto menu

:secrets
echo.
echo Setting secrets...
echo.
set /p gemini="Enter GEMINI_API_KEY: "
if not "%gemini%"=="" fly secrets set GEMINI_API_KEY="%gemini%"
echo.
set /p secret="Enter SECRET_KEY (or press Enter to generate): "
if "%secret%"=="" (
    echo Generating random secret key...
    fly secrets set SECRET_KEY="%RANDOM%%RANDOM%%RANDOM%%RANDOM%"
) else (
    fly secrets set SECRET_KEY="%secret%"
)
echo.
echo Secrets set!
pause
goto menu

:volume
echo.
echo Creating persistent volume...
fly volumes create clip_data --size 10 --region iad
echo.
pause
goto menu

:ssh
echo.
echo Connecting to machine...
fly ssh console
echo.
pause
goto menu

:end
echo.
echo Goodbye!
