@echo off
REM Frontend Environment Setup Script for Windows
REM This script reads environment variables and injects them into the frontend

setlocal enabledelayedexpansion

REM Set defaults if not provided
if not defined API_BASE_URL set "API_BASE_URL=http://localhost:8000/api/v1"
if not defined CALENDAR_NAME set "CALENDAR_NAME=My Timetable"
if not defined TIMEZONE set "TIMEZONE=UTC"

REM Create a JavaScript file with environment variables
(
    echo // Auto-generated environment configuration
    echo window.ENV_API_BASE_URL = '!API_BASE_URL!';
    echo window.ENV_CALENDAR_NAME = '!CALENDAR_NAME!';
    echo window.ENV_TIMEZONE = '!TIMEZONE!';
) > frontend\env-config.js

echo.
echo ✓ Environment configuration updated:
echo   API_BASE_URL: !API_BASE_URL!
echo   CALENDAR_NAME: !CALENDAR_NAME!
echo   TIMEZONE: !TIMEZONE!
echo.
