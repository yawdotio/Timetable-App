# Quick Reference: Configuring for Deployment

## Fastest Way to Deploy with Custom URLs

### Option 1: Environment Variables (Recommended)
```bash
# Set before running start.sh or start.bat
export API_BASE_URL=https://your-backend-api.com/api/v1
export CALENDAR_NAME="Your Organization"
export TIMEZONE=America/New_York

./start.sh
```

### Option 2: .env.frontend File
```bash
# 1. Create the file
cp .env.frontend.example .env.frontend

# 2. Edit it
# API_BASE_URL=https://your-backend-api.com/api/v1
# CALENDAR_NAME=Your Organization
# TIMEZONE=America/New_York

# 3. Run startup
./start.sh
```

### Option 3: Docker Compose
```yaml
version: '3'
services:
  backend:
    build: .
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/db
    ports:
      - "8000:8000"
  
  frontend:
    image: nginx
    volumes:
      - ./frontend:/usr/share/nginx/html
    environment:
      API_BASE_URL: http://backend:8000/api/v1
      CALENDAR_NAME: My Calendar
      TIMEZONE: UTC
    ports:
      - "80:80"
```

## What Gets Configured

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `API_BASE_URL` | Backend API endpoint | `http://localhost:8000/api/v1` | `https://api.example.com/api/v1` |
| `CALENDAR_NAME` | Default calendar name in form | `My Timetable` | `University Calendar` |
| `TIMEZONE` | Default timezone for events | `UTC` | `America/New_York` |

## Files You Need to Know

- `.env` - Backend configuration (your existing file)
- `.env.frontend.example` - Template for frontend config
- `.env.frontend` - Frontend config (create this or set env vars)
- `setup-env.sh` / `setup-env.bat` - Auto-run by start scripts
- `frontend/env-config.js` - Generated automatically at startup

## Common Deployment Scenarios

### Localhost Development
No changes needed, defaults work fine.

### Same Machine, Different Port
```bash
export API_BASE_URL=http://localhost:8000/api/v1
./start.sh
```

### Docker Network
```bash
export API_BASE_URL=http://backend:8000/api/v1
./start.sh
```

### Cloud Deployment (e.g., AWS, Heroku)
```bash
export API_BASE_URL=https://your-app-backend.herokuapp.com/api/v1
export CALENDAR_NAME="Cloud Calendar"
./start.sh
```

## Notes

- Changes to environment variables only take effect after running `setup-env.sh/bat` and restarting
- The `env-config.js` file is auto-generated and should NOT be committed to git
- Users can still change calendar name in the UI after deployment - the env variable just sets the default
- All changes can be made without recompiling or rebuilding the frontend
