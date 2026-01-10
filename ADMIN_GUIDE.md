# Admin Panel Guide

## Overview
The Timetable Generator now has an admin panel that restricts file upload, rename, and delete operations to authenticated administrators only. All other features remain publicly accessible.

## Features

### Admin-Only Operations
- **Upload Files**: Upload timetable files from local disk or URL
- **Save Calendars**: Save and name timetables for reuse
- **Rename Calendars**: Edit the name of saved timetables
- **Delete Calendars**: Remove saved timetables and uploads
- **Manage All Uploads**: View and delete all uploaded files
- **Manage All Calendars**: View, rename, and delete all saved calendars

### Public Features (No Authentication Required)
- **Calendar Generation**: Create calendar files from available timetables
- **Event Filtering**: Filter by level, search by course name
- **Calendar Subscriptions**: Subscribe to calendar feeds
- **View Saved Timetables**: Browse available calendars to use

## Setup

### 1. Default Credentials
The default admin credentials are:
- **Username**: `admin`
- **Password**: `admin123`

**IMPORTANT**: Change these credentials in production!

### 2. Customizing Credentials
Set credentials using environment variables:

```bash
# On Windows (Command Prompt)
set ADMIN_USERNAME=your_username
set ADMIN_PASSWORD=your_password

# On Windows (PowerShell)
$env:ADMIN_USERNAME="your_username"
$env:ADMIN_PASSWORD="your_password"

# On Linux/Mac
export ADMIN_USERNAME=your_username
export ADMIN_PASSWORD=your_password
```

Then start the server:
```bash
python -m uvicorn app.main:app --reload
```

## Usage

### For Admins

1. **Login to Admin Panel**
   - Click the "🔐 Admin" button in the header
   - Enter your username and password
   - Click "Login"

2. **Upload Timetables**
   - The "Step 1: Upload Your Timetable" section becomes available
   - Upload files directly or from a URL
   - Map columns and configure settings
   - Save the timetable with a name

3. **Manage Calendars**
   - Click the "Manage Calendars" tab in the admin panel
   - View all saved calendars
   - Rename or delete calendars as needed
   - Each action requires confirmation

4. **Manage Uploads**
   - Click the "Manage Uploads" tab in the admin panel
   - View all uploaded files
   - Delete files to free up space
   - Check file metadata and processing status

5. **Logout**
   - Click the "Logout" button in the admin panel
   - The upload section becomes hidden
   - Normal users can only use public features

### For Regular Users

1. **View Available Timetables**
   - The gallery shows all saved timetables that admins have created
   - Click "Use" on any timetable to generate a calendar

2. **Generate Calendars**
   - Use available timetables to create calendar files
   - Filter courses by level
   - Search for specific courses
   - Set reminder times
   - Download or subscribe to the calendar

3. **Subscribe to Calendars**
   - Generate a calendar feed URL
   - Subscribe in your calendar app (Google Calendar, Outlook, etc.)
   - Updates appear automatically

## API Endpoints

### Public Endpoints (No Auth Required)
- `GET /api/v1/calendar` - Get available timetables
- `POST /api/v1/calendar/generate` - Generate calendar file
- `GET /api/v1/subscription` - Get calendar feeds

### Admin-Only Endpoints (HTTP Basic Auth Required)
- `POST /api/v1/upload/file` - Upload file
- `POST /api/v1/upload/url` - Upload from URL
- `POST /api/v1/upload/save` - Save timetable
- `DELETE /api/v1/upload/{upload_id}` - Delete upload
- `DELETE /api/v1/upload/saved/{saved_id}` - Delete saved calendar
- `PUT /api/v1/upload/rename/{saved_id}` - Rename calendar
- `GET /api/v1/admin/uploads` - List all uploads
- `GET /api/v1/admin/saved-calendars` - List all calendars
- `POST /api/v1/admin/login` - Admin login verification

## Security Notes

### Current Implementation
- Uses HTTP Basic Authentication (username:password in Authorization header)
- Credentials are sent with each request
- **NOT suitable for production over HTTP** (not encrypted)

### Production Recommendations
1. **Use HTTPS Only**: Always run with SSL/TLS certificates
2. **Use Bearer Tokens**: Implement JWT or similar token-based auth
3. **Use Database**: Store hashed passwords in database with proper hashing (bcrypt, argon2)
4. **Add Session Management**: Implement proper session timeouts
5. **Rate Limiting**: Add rate limiting to prevent brute force attacks
6. **Audit Logging**: Log all admin actions
7. **API Keys**: Consider using API keys for programmatic access

## Troubleshooting

### "Invalid admin credentials" error
- Check your username and password
- Verify environment variables are set correctly (if using custom credentials)
- Restart the server if you changed environment variables

### Can't upload files
- Make sure you're logged in as admin
- Check that the file format is supported (PDF, Excel, CSV)
- Check server logs for detailed error messages

### Changes not appearing
- Refresh the admin panel after making changes
- Check browser console for errors (F12)
- Verify the request succeeded (look for "success" message)

## File Structure

### New Files
- `app/core/auth.py` - Authentication utilities
- `app/api/admin.py` - Admin endpoints
- `frontend/admin.js` - Admin panel JavaScript

### Modified Files
- `app/api/router.py` - Added admin router
- `app/api/upload.py` - Added auth checks to upload endpoints
- `frontend/index.html` - Added admin panel HTML
- `frontend/styles.css` - Added admin panel styles
- `frontend/app.js` - Updated upload handlers, added auth checks
