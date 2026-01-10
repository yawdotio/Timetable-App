# Timetable Generator API - Quick Start Guide

## 🚀 Getting Started (Fast Track)

### Windows
```bash
# Run the quick start script
start.bat
```

### macOS/Linux
```bash
# Make script executable and run
chmod +x start.sh
./start.sh
```

The script will:
1. Create a virtual environment
2. Install all dependencies
3. Set up the database
4. Start the development server

Access the API at: **http://localhost:8000/api/v1/docs**

---

## 📖 Manual Setup

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# 5. Initialize database
python init_db.py

# 6. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎯 Quick Test

Once the server is running, test with:

```bash
# Health check
curl http://localhost:8000/health

# Or visit in browser
http://localhost:8000/api/v1/docs
```

---

## 📚 Next Steps

1. **Upload a file**: Go to `/api/v1/docs` and try the `/upload/file` endpoint
2. **Read the full README**: See `README.md` for detailed documentation
3. **Build the frontend**: This is the backend API - you'll need to create a React/Vue frontend

---

## 🐛 Troubleshooting

**Import errors?**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Port 8000 already in use?**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

**Database errors?**
```bash
# Delete and recreate database
del timetable_generator.db  # Windows
rm timetable_generator.db   # macOS/Linux
python init_db.py
```

---

## 📦 What You Just Set Up

✅ FastAPI backend with automatic API documentation  
✅ File parsing for PDF, Excel, CSV  
✅ Calendar generation (.ics files)  
✅ Database for tracking uploads and subscriptions  
✅ RESTful API endpoints ready for frontend integration  

**Happy coding! 🎉**
