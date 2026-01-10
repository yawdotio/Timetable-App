# Timetable Generator - Project Summary

## 🎯 Project Overview

A FastAPI-based backend service that converts unstructured timetables (PDFs, Excel, CSV) into structured calendar files (.ics) with a human-in-the-loop verification workflow.

**Status**: Backend Complete ✅ | Frontend: Not Started

---

## 📁 Project Structure

```
Timetable Generator/
│
├── 📂 app/                          # Main application package
│   ├── 📂 api/                      # API endpoint routes
│   │   ├── __init__.py
│   │   ├── router.py               # Main router combining all routes
│   │   ├── upload.py               # File upload & parsing endpoints
│   │   ├── calendar.py             # Calendar generation endpoints
│   │   └── subscription.py         # Dynamic subscription management
│   │
│   ├── 📂 core/                     # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py               # Application settings (env vars)
│   │   └── database.py             # Database connection & session
│   │
│   ├── 📂 models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   └── subscription.py         # Subscription & UploadHistory models
│   │
│   ├── 📂 schemas/                  # Pydantic validation schemas
│   │   ├── __init__.py
│   │   └── event.py                # Request/response schemas
│   │
│   ├── 📂 utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── parser.py               # PDF/Excel/CSV parsing logic
│   │   └── calendar_generator.py  # .ics file generation
│   │
│   ├── __init__.py
│   └── main.py                     # FastAPI application entry point
│
├── 📂 uploads/                      # Temporary file storage
│   └── .gitkeep
│
├── 📂 tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py                 # Test configuration
│   └── test_api.py                 # API endpoint tests
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # Full documentation
├── 📄 QUICKSTART.md                 # Quick start guide
├── 📄 PROJECT_SUMMARY.md            # This file
├── 📄 init_db.py                    # Database initialization script
├── 📄 examples.py                   # Usage examples
├── 📄 setup.cfg                     # Test & linting configuration
├── 🦇 start.bat                     # Windows quick start script
└── 🐚 start.sh                      # Unix/macOS quick start script
```

---

## 🔧 Key Components

### 1. File Parsing (`app/utils/parser.py`)
**Purpose**: Extract structured data from various file formats

**Features**:
- ✅ PDF table extraction using `pdfplumber`
- ✅ Excel (.xlsx, .xls) parsing with `pandas`
- ✅ CSV parsing with multiple encoding support
- ✅ Fuzzy date parsing (handles "Jan 15", "15/01/2026", etc.)
- ✅ Time range extraction ("9:00 AM - 10:30 AM")

**Key Methods**:
- `parse_file()` - Main entry point
- `parse_pdf()` - PDF-specific parsing
- `parse_excel()` - Excel parsing
- `parse_csv()` - CSV parsing
- `fuzzy_date_parse()` - Flexible date parsing
- `extract_time()` - Time range extraction

### 2. Calendar Generation (`app/utils/calendar_generator.py`)
**Purpose**: Create iCalendar (.ics) files from event data

**Features**:
- ✅ Standard iCalendar format generation
- ✅ Timezone support
- ✅ Event duration handling
- ✅ UID generation for unique events

**Key Methods**:
- `generate_ics()` - Create .ics file content
- `generate_summary()` - Preview calendar statistics

### 3. Database Models (`app/models/subscription.py`)

#### Subscription Model
Stores dynamic calendar subscription configurations
```python
- id (UUID)
- name, description
- source_url, source_type
- parsing_rules (JSON)
- calendar_name, timezone
- is_active
- timestamps
```

#### UploadHistory Model
Tracks file upload processing
```python
- id (UUID)
- filename, file_type, file_size
- status (pending/processing/completed/failed)
- events_extracted
- timestamps
```

### 4. API Endpoints

#### Upload Endpoints (`/api/v1/upload`)
- `POST /file` - Upload and parse file
- `GET /status/{upload_id}` - Check processing status
- `DELETE /{upload_id}` - Delete upload

#### Calendar Endpoints (`/api/v1/calendar`)
- `POST /generate` - Generate calendar, return URL
- `POST /download` - Direct download .ics file
- `POST /preview` - Preview calendar statistics

#### Subscription Endpoints (`/api/v1/subscription`)
- `POST /` - Create subscription
- `GET /` - List all subscriptions
- `GET /{id}` - Get specific subscription
- `GET /{id}/calendar.ics` - Fetch dynamic calendar
- `PUT /{id}` - Update subscription
- `DELETE /{id}` - Delete subscription

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Framework** | FastAPI | High-performance web framework |
| **Database** | SQLAlchemy + SQLite/PostgreSQL | ORM and data persistence |
| **Validation** | Pydantic | Request/response validation |
| **PDF Parsing** | pdfplumber | Extract tables from PDFs |
| **Data Processing** | pandas | Excel/CSV handling |
| **Date Parsing** | python-dateutil | Flexible date parsing |
| **Calendar** | icalendar | .ics file generation |
| **Server** | Uvicorn | ASGI server |
| **Testing** | pytest | Test framework |

---

## 🚀 Quick Start

### Installation
```bash
# Clone/navigate to project
cd "c:\Users\YAWPC\OneDrive\Desktop\Dev\Timetable Generator"

# Run quick start script (Windows)
start.bat

# Or manually
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload
```

### Access Points
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## 📊 Current Status

### ✅ Completed (Weeks 1-5 of 8-week plan)

**Phase 1: Core Logic** ✅
- [x] Excel & CSV parsing
- [x] PDF parsing (with pdfplumber)
- [x] Fuzzy date parsing
- [x] ICS generation
- [x] Timezone handling

**Phase 2: API & Backend** ✅
- [x] FastAPI setup
- [x] Upload endpoint
- [x] Calendar generation endpoints
- [x] Database models
- [x] Dynamic subscription system
- [x] SQLAlchemy integration

### 🔜 Next Steps (Weeks 6-8)

**Phase 3: Frontend** 🚧
- [ ] React/Vue.js setup
- [ ] File upload drag-and-drop UI
- [ ] Column mapper component (crucial!)
- [ ] Event selection grid
- [ ] Calendar preview
- [ ] Subscription management UI

**Phase 4: Deployment** 🚧
- [ ] Docker configuration
- [ ] Railway/Render deployment
- [ ] Frontend deployment (Vercel/Netlify)
- [ ] Production database setup

**Enhancements** 📋
- [ ] OCR support for image-based PDFs
- [ ] LLM integration for complex parsing
- [ ] URL fetching for remote files
- [ ] User authentication
- [ ] Rate limiting
- [ ] Caching

---

## 🎓 Development Timeline

Based on the 8-week plan:

| Week | Phase | Status |
|------|-------|--------|
| 1-3 | Core Logic (Parsing & ICS) | ✅ Complete |
| 4-5 | API & Backend | ✅ Complete |
| 6-7 | Frontend UI | ⏳ Not Started |
| 8 | Testing & Deployment | ⏳ Not Started |

**Current Progress**: ~62% (5/8 weeks)

---

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View examples
python examples.py
```

---

## 📚 Key Files to Review

**For Backend Development**:
1. `app/main.py` - Application entry point
2. `app/api/router.py` - Route organization
3. `app/utils/parser.py` - Parsing logic
4. `app/utils/calendar_generator.py` - Calendar creation

**For Frontend Development**:
1. `app/schemas/event.py` - API contracts
2. `README.md` - API usage examples
3. `examples.py` - Sample data structures

**For Deployment**:
1. `.env.example` - Configuration template
2. `requirements.txt` - Dependencies
3. `README.md` - Deployment guide

---

## 🔑 Key Design Decisions

1. **Human-in-the-Loop**: Preview data before calendar generation
2. **Flexible Parsing**: Column mapping for various data structures
3. **Dynamic Subscriptions**: URLs that auto-update from sources
4. **SQLite Default**: Easy local development, PostgreSQL for production
5. **JSON Parsing Rules**: Flexible configuration storage

---

## 📖 Documentation

- **README.md**: Comprehensive documentation
- **QUICKSTART.md**: Fast setup guide
- **API Docs**: Auto-generated at `/api/v1/docs`
- **examples.py**: Usage examples
- **This file**: Project overview

---

## 🎯 Next Developer TODO

If you're continuing this project:

1. **Frontend Setup**:
   ```bash
   # Create React app
   npx create-react-app frontend
   # Or Vue
   npm create vue@latest frontend
   ```

2. **Key Frontend Components to Build**:
   - `FileUpload.jsx` - Drag-and-drop uploader
   - `ColumnMapper.jsx` - Map columns to fields (CRITICAL!)
   - `EventGrid.jsx` - Show/select events
   - `CalendarPreview.jsx` - Preview before download
   - `SubscriptionManager.jsx` - Manage dynamic links

3. **Frontend-Backend Integration**:
   - Use `axios` or `fetch` to call API
   - Handle file uploads with `FormData`
   - Display preview data in tables
   - Download .ics files

4. **Deployment**:
   - Backend: Railway/Render
   - Frontend: Vercel/Netlify
   - Database: PostgreSQL on Railway

---

## 💡 Tips for Next Developer

- **Column Mapper is Crucial**: This is where users fix parsing errors
- **Test with Real Data**: Try university timetables (usually messy PDFs)
- **Error Handling**: PDFs vary wildly, expect failures
- **Async Processing**: For large files, consider background jobs
- **LLM Integration**: GPT-4 Vision can help with messy PDFs

---

## 📞 Support

- Check `/api/v1/docs` for interactive API testing
- Run `python examples.py` for sample data
- See `README.md` for troubleshooting

---

**Project Created**: January 7, 2026  
**Backend Status**: Production Ready ✅  
**Frontend Status**: Not Started 🚧  
**Last Updated**: January 7, 2026
