# Timetable Generator API

A FastAPI-based backend for parsing timetables from PDFs/Excel files and generating iCalendar (.ics) files with a human-in-the-loop workflow.

## Features

✅ **Multiple File Format Support**
- PDF parsing using `pdfplumber`
- Excel (.xlsx, .xls) support via `pandas`
- CSV file processing

✅ **Smart Data Extraction**
- Automatic table detection in PDFs
- Fuzzy date parsing for various formats
- Time range extraction (start/end times)

✅ **Calendar Generation**
- Generate standard .ics calendar files
- Support for custom timezones
- **Download or subscribe to dynamic calendars**
- **Live subscription URLs that auto-update**

✅ **Recurring Events & Reminders**
- **Weekly, daily, and specific weekday recurrence**
- **45-minute reminders for all events**
- **Apply patterns to individual or all events**
- **Full iCalendar RRULE support**

✅ **Dynamic Subscriptions**
- Create subscription URLs that update automatically
- Store parsing rules for recurring data sources
- Manage multiple calendar feeds

✅ **Human-in-the-Loop Workflow**
- Preview extracted data before generating calendar
- Column mapping for flexible data structures
- Event selection/deselection capability
- **Per-event recurring pattern selection**

## Project Structure

```
Timetable Generator/
├── app/
│   ├── api/              # API endpoints
│   │   ├── upload.py     # File upload endpoints
│   │   ├── calendar.py   # Calendar generation endpoints
│   │   └── subscription.py  # Dynamic subscription management
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   └── database.py   # Database setup
│   ├── models/           # Database models
│   │   └── subscription.py
│   ├── schemas/          # Pydantic schemas
│   │   └── event.py
│   ├── utils/            # Utility functions
│   │   ├── parser.py     # File parsing logic
│   │   └── calendar_generator.py  # iCalendar generation
│   └── main.py           # FastAPI application
├── uploads/              # Temporary file storage
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- (Optional) PostgreSQL for production

### Setup Steps

1. **Clone the repository**
```bash
cd "c:\Users\YAWPC\OneDrive\Desktop\Dev\Timetable Generator"
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
copy .env.example .env
# Edit .env with your configuration
```

5. **Configure Google Cloud Storage** (for production/cloud deployment)
See [GCS_SETUP.md](GCS_SETUP.md) for detailed instructions.

For local development without GCS, set `USE_GCS=false` in your `.env` file.

6. **Initialize the database**
```bash
python -c "from app.core.database import init_db; init_db()"
```

## Running the Application

### Development Mode
```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main.py directly
python app/main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Frontend**: http://localhost:8080 (if running the HTML frontend)

## Deploying the Frontend to Vercel (Backend on Google Cloud)

1. **Expose the backend**: Deploy the FastAPI service to Google Cloud (Cloud Run or similar) and note the public URL ending in `/api/v1` (example: `https://timetable-generator-123.run.app/api/v1`).
2. **Allow CORS**: Add your Vercel domain (including the preview domain) to `CORS_ORIGINS` in the backend environment or keep the permissive default during testing.
3. **Set Vercel env vars**:
  - `API_BASE_URL` = your backend API base (must include `/api/v1`).
  - `CALENDAR_NAME` (optional) = default calendar display name.
  - `TIMEZONE` (optional) = default timezone (e.g., `UTC`).
4. **Build settings** (already in `vercel.json`):
  - Build command: `bash scripts/gen-env.sh` (creates `frontend/env-config.js`).
  - Output directory: `frontend`.
5. **Deploy**: Point Vercel at the repo or upload the `frontend` folder; Vercel will generate `env-config.js` from the env vars and serve the static site.
6. **Verify**: Open the deployed site; network calls should target `API_BASE_URL`. Hitting `https://<backend>/api/v1/config` should return JSON with `api_base_url`, `calendar_name`, and `timezone`.

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### 📤 File Upload

**POST** `/api/v1/upload/file`
- Upload PDF, Excel, or CSV file
- Returns preview data with detected columns
- Response includes `upload_id` for tracking

```bash
curl -X POST "http://localhost:8000/api/v1/upload/file" \
  -F "file=@timetable.pdf"
```

**GET** `/api/v1/upload/status/{upload_id}`
- Check processing status of uploaded file

### 📅 Calendar Generation

**POST** `/api/v1/calendar/generate`
- Generate calendar from events
- Returns download URL

**POST** `/api/v1/calendar/download`
- Directly download .ics file

**POST** `/api/v1/calendar/preview`
- Preview calendar without generating file

Request body example:
```json
{
  "events": [
    {
      "date": "2026-01-15",
      "time": "09:00",
      "title": "Morning Lecture",
      "location": "Room 101",
      "end_time": "10:30"
    }
  ],
  "calendar_name": "My Class Schedule",
  "timezone": "America/New_York"
}
```

### 🔗 Subscriptions (Dynamic Links)

**POST** `/api/v1/subscription/`
- Create a new subscription

**GET** `/api/v1/subscription/`
- List all subscriptions

**GET** `/api/v1/subscription/{id}`
- Get specific subscription details

**GET** `/api/v1/subscription/{id}/calendar.ics`
- Fetch dynamic calendar (this is the subscription URL)

**PUT** `/api/v1/subscription/{id}`
- Update subscription

**DELETE** `/api/v1/subscription/{id}`
- Delete subscription

## Usage Examples
Using the Frontend (Easiest)

1. **Start the backend** (in one terminal):
```bash
cd "c:/Users/YAWPC/OneDrive/Desktop/Dev/Timetable Generator"
.venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

2. **Start the frontend** (in another terminal):
```bash
cd "c:/Users/YAWPC/OneDrive/Desktop/Dev/Timetable Generator/frontend"
python -m http.server 8080
```

3. **Open in browser**: http://localhost:8080

4. **Follow the workflow**:
   - Upload your timetable file
   - Map columns (auto-detected!)
   - Select events to include
   - Choose: Download .ics OR Create subscription link
   - Add subscription to Google Calendar/Outlook/Apple Calendar

### Using the API Directly

#### 
### 1. Upload and Parse a File

```python
import requests

url = "http://localhost:8000/api/v1/upload/file"
files = {"file": open("timetable.pdf", "rb")}

response = requests.post(url, files=files)
data = response.json()

print(f"Upload ID: {data['upload_id']}")
print(f"Detected columns: {data['detected_columns']}")
print(f"Preview data: {data['preview_data'][:5]}")  # First 5 rows
```

### 2. Generate Calendar

```python
import requests

url = "http://localhost:8000/api/v1/calendar/download"

events = [
    {
        "date": "2026-01-20",
        "time": "14:00",
        "title": "Team Meeting",
        "location": "Conference Room A"
    },
    {
        "date": "2026-01-21",
        "time": "09:00",
        "title": "Project Presentation",
        "location": "Main Hall"
    }
]

response = requests.post(url, json={
    "events": events,
    "calendar_name": "Work Schedule",
    "timezone": "UTC"
})

# Save calendar file
with open("schedule.ics", "wb") as f:
    f.write(response.content)
```

### 3. Create Dynamic Subscription

```python
import requests

url = "http://localhost:8000/api/v1/subscription/"

subscription_data = {
    "name": "University Exam Schedule",
    "description": "Auto-updating exam timetable",
    "source_url": "https://example.com/exam-schedule.xlsx",
    "source_type": "excel",
    "parsing_rules": {
        "date_column": "Exam Date",
        "time_column": "Time",
        "title_column": "Course",
        "location_column": "Room"
    },
    "calendar_name": "Exam Schedule",
    "timezone": "America/New_York"
}

response = requests.post(url, json=subscription_data)
subscription = response.json()

# This URL can be added to any calendar app
calendar_url = f"http://localhost:8000/api/v1/subscription/{subscription['id']}/calendar.ics"
print(f"Subscribe to: {calendar_url}")
```

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Configuration

Edit `.env` file to customize:

```env
# Database (SQLite for development, PostgreSQL for production)
DATABASE_URL=sqlite:///./timetable_generator.db

# API Settings
PROJECT_NAME=Timetable Generator API
API_V1_STR=/api/v1

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads

# Calendar Settings
TIMEZONE=UTC
```

## Deployment

### Using Docker (Coming Soon)

```dockerfile
# Dockerfile example
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy to Railway/Render

1. Push code to GitHub
2. Connect repository to Railway/Render
3. Set environment variables
4. Deploy!

## Development Roadmap

### Phase 1: Core Logic ✅ (Completed)
- [x] File parsing (PDF, Excel, CSV)
- [x] iCalendar generation
- [x] Fuzzy date/time parsing

### Phase 2: API & Backend ✅ (Completed)
- [x] Upload endpoint
- [x] Calendar generation endpoint
- [x] Dynamic subscription management
- [x] Database models

### Phase 3: Frontend (Next Steps)
- [ ] React/Vue frontend
- [ ] Drag-and-drop file upload
- [ ] Column mapper UI
- [ ] Event selection interface
- [ ] Dynamic link management

### Phase 4: Enhancement (Future)
- [ ] OCR support for image-based PDFs
- [ ] LLM integration for better parsing
- [ ] URL fetching for remote files
- [ ] User authentication
- [ ] Rate limiting
- [ ] Caching layer

## Troubleshooting

### Common Issues

1. **PDF parsing fails**
   - Try different PDF tools (pypdf vs pdfplumber)
   - For image-based PDFs, install Tesseract OCR

2. **Date parsing errors**
   - Check date format in source file
   - Update parsing rules in subscription

3. **Database errors**
   - Delete `timetable_generator.db` and reinitialize
   - Check DATABASE_URL in .env

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/api/v1/docs`
- Review comprehensive guides:
  - [COMPLETE_GUIDE.md](./COMPLETE_GUIDE.md) - Full system documentation
  - [SUBSCRIPTION_GUIDE.md](./SUBSCRIPTION_GUIDE.md) - Live subscription setup
  - [RECURRING_EVENTS_GUIDE.md](./RECURRING_EVENTS_GUIDE.md) - Recurring events & reminders

---

**Built with ❤️ using FastAPI**
