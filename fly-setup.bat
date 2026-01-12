@echo off
REM Fly.io Setup Script for Clip Generator

echo ========================================
echo Clip Generator - Fly.io Setup Wizard
echo ========================================
echo.

cd /d "%~dp0"

REM Check if fly CLI is installed
where fly >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fly CLI not found!
    echo.
    echo Please install it first:
    echo   PowerShell: iwr https://fly.io/install.ps1 -useb ^| iex
    echo   Or visit: https://fly.io/docs/hands-on/install-flyctl/
    echo.
    pause
    exit /b 1
)

echo ✓ Fly CLI found
echo.

REM Check if logged in
fly auth whoami >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo You need to log in to Fly.io first.
    echo.
    set /p login="Log in now? (y/n): "
    if /i "%login%"=="y" (
        fly auth login
    ) else (
        echo Please run: fly auth login
        pause
        exit /b 1
    )
)

echo ✓ Logged in to Fly.io
echo.

echo ========================================
echo Step 1: App Configuration
echo ========================================
echo.

set /p appname="Enter app name (or press Enter for 'clip-generator'): "
if "%appname%"=="" set appname=clip-generator

echo.
echo Available regions:
echo   iad - US East (Virginia)
echo   ord - US Central (Chicago)
echo   lax - US West (Los Angeles)
echo   lhr - Europe (London)
echo   fra - Europe (Frankfurt)
echo   syd - Asia Pacific (Sydney)
echo.
set /p region="Enter region (or press Enter for 'iad'): "
if "%region%"=="" set region=iad

echo.
echo ========================================
echo Step 2: API Keys
echo ========================================
echo.

echo You need a Gemini API key from Google AI Studio
echo Visit: https://makersuite.google.com/app/apikey
echo.
set /p gemini="Enter your GEMINI_API_KEY: "

if "%gemini%"=="" (
    echo ERROR: GEMINI_API_KEY is required!
    pause
    exit /b 1
)

echo.
echo Generating random SECRET_KEY...
set SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%%RANDOM%

echo.
echo ========================================
echo Step 3: Optional Services
echo ========================================
echo.

set /p usedb="Do you want to add PostgreSQL database? (y/n): "
set /p usestorage="Do you want to configure cloud storage? (y/n): "

echo.
echo ========================================
echo Step 4: Creating App
echo ========================================
echo.

echo Creating Fly.io app: %appname%
fly apps create %appname% --org personal

echo.
echo Setting secrets...
fly secrets set GEMINI_API_KEY="%gemini%" SECRET_KEY="%SECRET_KEY%" -a %appname%

echo.
echo Creating persistent volume...
fly volumes create clip_data --size 10 --region %region% -a %appname%

if /i "%usedb%"=="y" (
    echo.
    echo Creating PostgreSQL database...
    fly postgres create --name %appname%-db --region %region%
    echo.
    echo Attaching database...
    fly postgres attach %appname%-db -a %appname%
)

if /i "%usestorage%"=="y" (
    echo.
    echo Cloud Storage Configuration
    echo.
    set /p bucket="Storage bucket name: "
    set /p accesskey="Access key: "
    set /p secretkey="Secret key: "
    set /p endpoint="Endpoint URL (leave empty for AWS S3): "
    
    fly secrets set STORAGE_BUCKET="%bucket%" STORAGE_ACCESS_KEY="%accesskey%" STORAGE_SECRET_KEY="%secretkey%" -a %appname%
    
    if not "%endpoint%"=="" (
        fly secrets set STORAGE_ENDPOINT="%endpoint%" -a %appname%
    )
)

echo.
echo ========================================
echo Step 5: Deploying
echo ========================================
echo.

echo Deploying your app to Fly.io...
echo This may take a few minutes...
echo.

fly deploy -a %appname%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! 🎉
    echo ========================================
    echo.
    echo Your app is now live at: https://%appname%.fly.dev
    echo.
    echo Useful commands:
    echo   fly logs -a %appname%          - View logs
    echo   fly status -a %appname%        - Check status
    echo   fly open -a %appname%          - Open in browser
    echo   fly ssh console -a %appname%   - SSH into machine
    echo.
    echo Opening your app...
    timeout /t 3 >nul
    fly open -a %appname%
) else (
    echo.
    echo ========================================
    echo Deployment failed!
    echo ========================================
    echo.
    echo Check the logs above for errors.
    echo Common issues:
    echo   - Invalid API keys
    echo   - App name already taken
    echo   - Network issues
    echo.
    echo Try running: fly logs -a %appname%
)

echo.
pause
