@echo off
echo ========================================
echo Timetable Generator - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Setting up frontend environment configuration...
call setup-env.bat
if errorlevel 1 (
    echo Warning: Failed to setup environment (non-critical)
)

echo.
echo Setting up environment...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file from .env.example
)

echo.
echo Initializing database...
python init_db.py
if errorlevel 1 (
    echo Error: Failed to initialize database
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Starting the server...
echo API will be available at: http://localhost:8000
echo Interactive docs at: http://localhost:8000/api/v1/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
