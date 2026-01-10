# Timetable Generator - Frontend

Pure HTML/CSS/JavaScript frontend for the Timetable Generator.

## Features

✅ **Drag & Drop File Upload**
- Upload PDF, Excel, or CSV files
- Visual drag-and-drop interface

✅ **Smart Column Mapping**
- Auto-detect common column names
- Manual column selection
- Map date, time, title, location, etc.

✅ **Event Selection Grid**
- Review all extracted events
- Select/deselect individual events
- Select all / deselect all

✅ **Calendar Generation**
- Generate .ics calendar files
- Custom calendar name
- Timezone selection
- Direct download

## Usage

### Option 1: Serve with Python (Recommended)

```bash
# From the frontend directory
cd frontend
python -m http.server 8080
```

Then open: http://localhost:8080

### Option 2: Open Directly

Simply open `index.html` in your browser. Note: Some browsers may block API calls due to CORS when opening files directly. Use the Python server method instead.

### Option 3: Serve from FastAPI

The backend can serve the frontend:

```python
# Add to app/main.py
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

Then access at: http://localhost:8000

## API Requirements

The frontend expects the FastAPI backend to be running at:
- **URL**: http://localhost:8000
- **Endpoints**:
  - `POST /api/v1/upload/file`
  - `POST /api/v1/calendar/generate`
  - `POST /api/v1/calendar/download`

## Workflow

1. **Upload**: Drag & drop or select a timetable file
2. **Map**: Choose which columns contain dates, times, titles, etc.
3. **Select**: Review and select which events to include
4. **Choose Option**:
   - **Download**: Get a static .ics file (one-time)
   - **Subscribe**: Create a live calendar link (auto-updates)
5. **Add to Calendar**: Import .ics or subscribe to the live URL

## 🔗 Live Subscriptions

The subscription feature creates a **dynamic calendar URL** that:
- Works with Google Calendar, Apple Calendar, Outlook
- Auto-updates when your timetable changes (if source URL provided)
- Can be shared with others
- Managed from the "My Subscriptions" page

**Example Subscription URL**:
```
http://localhost:8000/api/v1/subscription/abc-123/calendar.ics
```

Add this to any calendar app and it stays synced!

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styling
├── app.js          # Application logic
└── README.md       # This file
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Customization

### Change API URL

Edit `API_BASE_URL` in `app.js`:

```javascript
const API_BASE_URL = 'https://your-api.com/api/v1';
```

### Modify Colors

Edit CSS variables in `styles.css`:

```css
:root {
    --primary: #4f46e5;
    --success: #10b981;
    /* ... */
}
```

## No Build Required!

This is pure HTML/CSS/JS - no npm, webpack, or build tools needed. Just open and use!
