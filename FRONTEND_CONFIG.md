# Frontend Configuration Guide

This guide explains how to configure the frontend for different deployment environments.

## Overview

The frontend can be configured without recompiling or rebuilding through environment variables. Configuration is loaded at runtime from the `env-config.js` file, which is generated automatically during startup.

## Configuration Variables

### `API_BASE_URL` (Required)
The backend API endpoint URL. This is where the frontend sends all API requests.

**Examples:**
- Local development: `http://localhost:8000/api/v1`
- Docker: `http://backend:8000/api/v1`
- Production: `https://api.example.com/api/v1`

### `CALENDAR_NAME` (Optional)
The default calendar name shown in the calendar settings form.

**Default:** `My Timetable`

**Examples:**
- `University Calendar`
- `Spring 2026 Schedule`
- `Class Schedule`

### `TIMEZONE` (Optional)
The default timezone for calendar events.

**Default:** `UTC`

**Valid timezones:**
- `UTC` (Coordinated Universal Time)
- `America/New_York` (Eastern Time)
- `America/Chicago` (Central Time)
- `America/Denver` (Mountain Time)
- `America/Los_Angeles` (Pacific Time)
- `Europe/London` (London)
- `Europe/Paris` (Paris)
- `Asia/Tokyo` (Tokyo)
- `Australia/Sydney` (Sydney)

## How to Configure

### Method 1: Environment Variables (Recommended for Docker/Cloud Deployments)

Set environment variables before running the startup script:

**Linux/Mac:**
```bash
export API_BASE_URL=https://api.example.com/api/v1
export CALENDAR_NAME="University Schedule"
export TIMEZONE="America/New_York"
./start.sh
```

**Windows (Command Prompt):**
```batch
set API_BASE_URL=https://api.example.com/api/v1
set CALENDAR_NAME=University Schedule
set TIMEZONE=America/New_York
start.bat
```

**Windows (PowerShell):**
```powershell
$env:API_BASE_URL = "https://api.example.com/api/v1"
$env:CALENDAR_NAME = "University Schedule"
$env:TIMEZONE = "America/New_York"
.\start.bat
```

### Method 2: .env.frontend File (Recommended for Local Development)

1. Copy the example file:
   ```bash
   cp .env.frontend.example .env.frontend
   ```

2. Edit `.env.frontend` with your values:
   ```
   API_BASE_URL=http://localhost:8000/api/v1
   CALENDAR_NAME=My Timetable
   TIMEZONE=UTC
   ```

3. Run the startup script (it will automatically load these values):
   ```bash
   ./start.sh  # Linux/Mac
   # or
   start.bat   # Windows
   ```

### Method 3: Docker Environment Variables

When running in Docker, pass environment variables at runtime:

```bash
docker run \
  -e API_BASE_URL=http://api-service:8000/api/v1 \
  -e CALENDAR_NAME="Docker Calendar" \
  -e TIMEZONE="UTC" \
  -p 3000:3000 \
  timetable-generator-frontend
```

Or in `docker-compose.yml`:

```yaml
services:
  frontend:
    environment:
      API_BASE_URL: http://backend:8000/api/v1
      CALENDAR_NAME: My Timetable
      TIMEZONE: UTC
```

## Configuration File Generation

The startup scripts automatically generate `frontend/env-config.js` from environment variables:

**Linux/Mac:**
```bash
bash setup-env.sh
```

**Windows:**
```batch
setup-env.bat
```

This creates a file like:
```javascript
// Auto-generated environment configuration
window.ENV_API_BASE_URL = 'http://localhost:8000/api/v1';
window.ENV_CALENDAR_NAME = 'My Timetable';
window.ENV_TIMEZONE = 'UTC';
```

## User Customization

Users can override the calendar name during usage:
- The `CALENDAR_NAME` environment variable sets the **default** value
- Users can change it in the "Calendar Settings" section before downloading
- The frontend allows full customization without redeployment

## Deployment Checklist

- [ ] Set `API_BASE_URL` to your backend service
- [ ] (Optional) Set `CALENDAR_NAME` for your organization
- [ ] (Optional) Set `TIMEZONE` for your region
- [ ] Run the startup script to generate `env-config.js`
- [ ] Verify the frontend loads correctly
- [ ] Test API calls to the backend URL

## Troubleshooting

### Issue: Frontend can't reach backend
**Solution:** Check that `API_BASE_URL` is correct and the backend service is accessible

### Issue: CORS errors
**Solution:** Make sure your frontend URL is added to the backend's `CORS_ORIGINS` setting

### Issue: env-config.js not found
**Solution:** Run `setup-env.sh` (or `setup-env.bat` on Windows) to generate it

## Files Reference

- `.env.frontend.example` - Template for frontend configuration
- `setup-env.sh` - Linux/Mac script to generate env-config.js
- `setup-env.bat` - Windows script to generate env-config.js
- `frontend/env-config.js` - Generated at runtime (not committed to git)
