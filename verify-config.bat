@echo off
REM Verification script for frontend configuration setup (Windows)

echo.
echo ========================================
echo Frontend Configuration Verification
echo ========================================
echo.

REM Check if env-config.js exists
if exist "frontend\env-config.js" (
    echo ✓ frontend\env-config.js exists
    echo   Content:
    type frontend\env-config.js | findstr /R "^"
) else (
    echo ✗ frontend\env-config.js not found
    echo   Run: setup-env.bat
)

echo.

REM Check if setup scripts exist
if exist "setup-env.bat" (
    echo ✓ setup-env.bat found
) else (
    echo ✗ setup-env.bat not found
)

if exist "setup-env.sh" (
    echo ✓ setup-env.sh found
) else (
    echo ✗ setup-env.sh not found
)

echo.

REM Check environment variables
echo Current Environment Variables:
echo   API_BASE_URL=%API_BASE_URL%
echo   CALENDAR_NAME=%CALENDAR_NAME%
echo   TIMEZONE=%TIMEZONE%

echo.

REM Check if app.js uses the variables
findstr /M "window.ENV_API_BASE_URL" frontend\app.js >nul
if %errorlevel% equ 0 (
    echo ✓ app.js uses ENV_API_BASE_URL
) else (
    echo ✗ app.js does not use ENV_API_BASE_URL
)

findstr /M "window.ENV_CALENDAR_NAME" frontend\app.js >nul
if %errorlevel% equ 0 (
    echo ✓ app.js uses ENV_CALENDAR_NAME
) else (
    echo ✗ app.js does not use ENV_CALENDAR_NAME
)

echo.
echo ========================================
echo To generate env-config.js with your settings:
echo ========================================
echo.
echo Option 1: Using environment variables
echo   set API_BASE_URL=http://localhost:8000/api/v1
echo   set CALENDAR_NAME=My Calendar
echo   set TIMEZONE=UTC
echo   setup-env.bat
echo.
echo Option 2: Using .env.frontend file
echo   copy .env.frontend.example .env.frontend
echo   REM Edit .env.frontend with your values
echo   setup-env.bat
echo.
