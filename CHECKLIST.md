# Timetable Generator - Setup Checklist

## ✅ Setup Checklist

### Initial Setup
- [ ] Python 3.8+ installed
- [ ] Git initialized (already done ✅)
- [ ] Navigate to project directory

### Quick Start (Recommended)
```bash
# Windows
start.bat

# macOS/Linux
chmod +x start.sh
./start.sh
```

### Manual Setup
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment:
  - Windows: `venv\Scripts\activate`
  - macOS/Linux: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Copy environment file: `copy .env.example .env` (or `cp` on Unix)
- [ ] Initialize database: `python init_db.py`
- [ ] Start server: `uvicorn app.main:app --reload`

### Verification
- [ ] Visit http://localhost:8000 (should show welcome message)
- [ ] Visit http://localhost:8000/health (should return `{"status": "healthy"}`)
- [ ] Visit http://localhost:8000/api/v1/docs (should show Swagger UI)
- [ ] Test upload endpoint in Swagger UI
- [ ] Test calendar preview endpoint

### Optional: Run Tests
- [ ] Run: `pytest tests/ -v`
- [ ] All tests should pass

### Optional: PostgreSQL Setup (Production)
- [ ] Install PostgreSQL
- [ ] Create database: `createdb timetable_generator`
- [ ] Update `.env`: `DATABASE_URL=postgresql://user:pass@localhost/timetable_generator`
- [ ] Run: `python init_db.py`

---

## 🚀 What's Working

### Backend API ✅
- ✅ File upload (PDF, Excel, CSV)
- ✅ File parsing with preview
- ✅ Calendar generation (.ics)
- ✅ Calendar download
- ✅ Dynamic subscriptions
- ✅ Database persistence
- ✅ Auto-generated API docs

### Core Features ✅
- ✅ PDF table extraction
- ✅ Excel/CSV parsing
- ✅ Fuzzy date parsing
- ✅ Time range extraction
- ✅ iCalendar generation
- ✅ Timezone support
- ✅ Error handling

---

## 🔜 What's Next

### Frontend (Not Started)
- [ ] Set up React/Vue project
- [ ] Create file upload UI
- [ ] Build column mapper component
- [ ] Create event selection grid
- [ ] Add calendar preview
- [ ] Implement subscription management

### Enhancements
- [ ] Add user authentication
- [ ] Implement rate limiting
- [ ] Add caching layer
- [ ] OCR for image PDFs
- [ ] LLM integration for complex parsing
- [ ] URL fetching for remote files

### Deployment
- [ ] Create Dockerfile
- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Set up production database
- [ ] Configure environment variables

---

## 📝 Quick Reference

### Run Development Server
```bash
uvicorn app.main:app --reload
```

### Run Tests
```bash
pytest tests/ -v
```

### View Examples
```bash
python examples.py
```

### Reset Database
```bash
# Windows
del timetable_generator.db
# macOS/Linux
rm timetable_generator.db

# Then reinitialize
python init_db.py
```

---

## 🐛 Common Issues & Solutions

### Issue: Import errors
**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 8000 in use
**Solution**:
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: Database locked
**Solution**:
```bash
# Stop all running servers
# Delete and recreate database
del timetable_generator.db  # Windows
rm timetable_generator.db   # macOS/Linux
python init_db.py
```

### Issue: PDF parsing fails
**Solution**:
- Check if PDF has actual tables (not images)
- Try different PDF files
- Consider using OCR for image-based PDFs

### Issue: Date parsing errors
**Solution**:
- Check date format in source file
- Try different date formats
- Manually specify date format in parsing rules

---

## 📚 Documentation Links

- **Full Docs**: `README.md`
- **Quick Start**: `QUICKSTART.md`
- **Project Overview**: `PROJECT_SUMMARY.md`
- **API Docs**: http://localhost:8000/api/v1/docs (when server running)
- **Examples**: `examples.py`

---

## 🎯 Current Status

**Completed**: Backend API (Weeks 1-5 of 8-week plan)  
**Next**: Frontend Development (Weeks 6-7)  
**Progress**: ~62% complete

---

## ✨ Features Ready to Use

1. **Upload Files**: POST to `/api/v1/upload/file`
2. **Preview Data**: Check response from upload
3. **Generate Calendar**: POST to `/api/v1/calendar/download`
4. **Create Subscription**: POST to `/api/v1/subscription/`
5. **Dynamic Calendar URL**: GET `/api/v1/subscription/{id}/calendar.ics`

---

**Last Updated**: January 7, 2026  
**Status**: Backend Complete ✅ | Ready for Frontend Development
