# Configuration Summary

## What Was Changed

### 1. Environment Variable Support
The frontend now supports configuration via environment variables that can be set during deployment:

- **`API_BASE_URL`**: Backend API endpoint (e.g., `http://localhost:8000/api/v1`)
- **`CALENDAR_NAME`**: Default calendar name (e.g., `My Timetable`)
- **`TIMEZONE`**: Default timezone (e.g., `UTC`)

### 2. Files Created/Modified

**New Files:**
- `frontend/env-config.js` - Generated at runtime with environment values
- `frontend/config.js` - Configuration template (for reference)
- `setup-env.sh` - Linux/Mac script to generate env-config.js
- `setup-env.bat` - Windows script to generate env-config.js
- `.env.frontend.example` - Template for frontend configuration
- `FRONTEND_CONFIG.md` - Comprehensive deployment guide

**Modified Files:**
- `frontend/index.html` - Added env-config.js script tag
- `frontend/app.js` - Uses window.ENV_* variables with fallbacks
- `start.sh` - Runs setup-env.sh before starting
- `start.bat` - Runs setup-env.bat before starting
- `.env` - Added documentation for frontend variables
- `.gitignore` - Added env-config.js to ignore list

### 3. How It Works

1. **At startup**, the setup scripts read environment variables and generate `frontend/env-config.js`
2. **Frontend loads** `env-config.js` which sets window variables
3. **JavaScript uses** those window variables or falls back to defaults
4. **Users can customize** the calendar name in the UI during usage

### 4. Deployment Examples

**Local Development:**
```bash
./start.sh  # Uses defaults or .env.frontend
```

**Docker with custom backend:**
```bash
export API_BASE_URL=http://backend:8000/api/v1
export CALENDAR_NAME="University Calendar"
./start.sh
```

**Docker Compose:**
```yaml
services:
  frontend:
    environment:
      API_BASE_URL: http://backend:8000/api/v1
      CALENDAR_NAME: My University
      TIMEZONE: America/New_York
```

### 5. Calendar Name Customization

- **Deployment default**: Set via `CALENDAR_NAME` environment variable
- **User override**: Users can change it in "Calendar Settings" before downloading
- **No recompilation needed**: Change the environment variable and restart

## Benefits

✅ No hardcoded URLs - all configurable  
✅ Easy deployment to different environments  
✅ Environment variables or .env.frontend file supported  
✅ Users can still customize during usage  
✅ Complete documentation in FRONTEND_CONFIG.md  
