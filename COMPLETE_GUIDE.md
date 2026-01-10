# 🚀 Complete System - Quick Start

## What You Have Now

✅ **Backend API** - FastAPI with file parsing and calendar generation  
✅ **Frontend UI** - Pure HTML/CSS/JS with drag-and-drop upload  
✅ **Live Subscriptions** - Dynamic calendar URLs that auto-update  
✅ **Database** - SQLite storing subscriptions and upload history  

---

## 🎯 Start Everything

### Terminal 1: Backend API
```bash
cd "c:/Users/YAWPC/OneDrive/Desktop/Dev/Timetable Generator"
.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```
**Running on**: http://localhost:8000

### Terminal 2: Frontend UI
```bash
cd "c:/Users/YAWPC/OneDrive/Desktop/Dev/Timetable Generator/frontend"
python -m http.server 8080
```
**Running on**: http://localhost:8080

---

## 📖 Complete User Flow

### Option 1: One-Time Download

1. Open http://localhost:8080
2. Upload `sample_timetable.csv`
3. Review auto-detected column mappings
4. Select events to include
5. Click **"Download Now"**
6. Import the .ics file into your calendar app

**Use Case**: One-off events, static schedules

### Option 2: Live Subscription

1. Open http://localhost:8080
2. Upload your timetable file
3. Review and select events
4. Click **"Create Subscription"**
5. Fill in details:
   - Name: "My Classes"
   - Description: Optional
   - Source URL: (Optional) URL to auto-fetch from
6. Copy the subscription URL
7. Add to Google Calendar/Outlook/Apple Calendar

**Use Case**: Schedules that change, shared calendars

---

## 🔗 Adding Subscription to Calendar Apps

### Google Calendar
```
1. Google Calendar → "+" next to "Other calendars"
2. "From URL"
3. Paste: http://localhost:8000/api/v1/subscription/{id}/calendar.ics
4. Add calendar
```

### Apple Calendar
```
1. File → New Calendar Subscription
2. Paste the subscription URL
3. Subscribe
```

### Outlook
```
1. Add calendar → From internet
2. Paste the subscription URL
3. Import
```

---

## 📚 Manage Subscriptions

Click **"📚 My Subscriptions"** in the header to:
- View all subscriptions
- Copy subscription links
- Download as .ics files
- Delete old subscriptions

---

## 🎨 Features Showcase

### Smart Column Detection
The system auto-detects columns like:
- "Date" → Date column
- "Time" → Time column  
- "Course"/"Event"/"Title" → Title column
- "Room"/"Location" → Location column

### Drag & Drop Upload
- Drag files directly onto the page
- Visual feedback with animations
- Instant validation

### Event Selection Grid
- Table view of all events
- Checkboxes to include/exclude
- Select All / Deselect All buttons
- Live counter

### Two-Option Download
Side-by-side cards:
- 📥 **One-Time Download** - Static .ics file
- 🔗 **Live Subscription** - Dynamic URL

---

## 📝 Test Files Included

**sample_timetable.csv**
```csv
Date,Time,Course,Room,Instructor
2026-01-20,09:00-10:30,Mathematics 101,A-201,Dr. Smith
2026-01-20,11:00-12:30,Physics Lab,B-105,Prof. Johnson
...
```

Upload this to test the full workflow!

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI + Python 3.12 |
| Database | SQLAlchemy + SQLite |
| Parsing | pdfplumber, pandas, pypdf |
| Calendar | icalendar, pytz |
| Frontend | Pure HTML/CSS/JavaScript |
| Server | Uvicorn (backend) + http.server (frontend) |

---

## 📊 API Endpoints

**Upload & Parse**
- `POST /api/v1/upload/file` - Upload file
- `GET /api/v1/upload/status/{id}` - Check status

**Calendar Generation**
- `POST /api/v1/calendar/generate` - Generate calendar
- `POST /api/v1/calendar/download` - Download .ics
- `POST /api/v1/calendar/preview` - Preview summary

**Subscriptions**
- `POST /api/v1/subscription/` - Create subscription
- `GET /api/v1/subscription/` - List all subscriptions
- `GET /api/v1/subscription/{id}` - Get subscription details
- `GET /api/v1/subscription/{id}/calendar.ics` - **Live calendar feed**
- `PUT /api/v1/subscription/{id}` - Update subscription
- `DELETE /api/v1/subscription/{id}` - Delete subscription

---

## 🎯 Key Features

### Backend
✅ PDF table extraction (pdfplumber)  
✅ Excel/CSV parsing (pandas)  
✅ Fuzzy date parsing (handles multiple formats)  
✅ Time range extraction  
✅ iCalendar generation  
✅ Timezone support  
✅ Database persistence  
✅ RESTful API with auto-docs  

### Frontend
✅ Drag-and-drop upload  
✅ Auto-column detection  
✅ Interactive event selection  
✅ Two-option workflow (download vs subscribe)  
✅ Subscription management UI  
✅ Copy-to-clipboard for links  
✅ Responsive design  
✅ No build tools required  

---

## 📖 Documentation

- **README.md** - Full project documentation
- **QUICKSTART.md** - Setup instructions
- **SUBSCRIPTION_GUIDE.md** - Live subscription tutorial
- **DEPLOYMENT.md** - Production deployment guide
- **frontend/README.md** - Frontend-specific docs

---

## 🎓 Next Steps

### For Users
1. Test with your own timetables
2. Create subscriptions for recurring schedules
3. Share subscription links with classmates/team

### For Developers
1. Add OCR for image-based PDFs
2. Implement LLM parsing for complex layouts
3. Add user authentication
4. Deploy to production (Railway/Render)
5. Build mobile app using the API

---

## 🆘 Troubleshooting

**Backend not starting?**
```bash
# Check Python environment
.venv/Scripts/python.exe --version

# Reinstall dependencies
.venv/Scripts/pip.exe install -r requirements.txt --force-reinstall
```

**Frontend CORS errors?**
- Make sure backend is running on port 8000
- Check `API_BASE_URL` in app.js

**Subscriptions not updating?**
- Calendar apps cache data (may take hours)
- Try removing and re-adding the subscription

---

## ✨ What Makes This Special

1. **Human-in-the-Loop** - User verifies before generating
2. **Smart Parsing** - Auto-detects common column patterns
3. **Two Workflows** - One-time download OR live subscription
4. **No Build Tools** - Pure HTML/CSS/JS frontend
5. **Production Ready** - Complete API, DB, and UI

---

**Enjoy your automated timetable calendar! 🎉**
