# Deployment Guide

## 🐳 Docker Deployment

### Local Docker Setup

1. **Build and run with Docker Compose**:
```bash
docker-compose up --build
```

The API will be available at http://localhost:8000

2. **Run in detached mode**:
```bash
docker-compose up -d
```

3. **View logs**:
```bash
docker-compose logs -f api
```

4. **Stop containers**:
```bash
docker-compose down
```

---

## ☁️ Cloud Deployment

### Option 1: Railway

1. **Sign up** at [railway.app](https://railway.app)

2. **Create new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Add PostgreSQL**:
   - Click "New" → "Database" → "PostgreSQL"
   - Railway will create `DATABASE_URL` automatically

4. **Configure environment variables**:
   - Go to your service → Variables
   - Add:
     ```
     PROJECT_NAME=Timetable Generator API
     API_V1_STR=/api/v1
     CORS_ORIGINS=["https://your-frontend.vercel.app"]
     TIMEZONE=UTC
     ```

5. **Deploy**:
   - Railway will auto-deploy on push to main branch

### Option 2: Render

1. **Sign up** at [render.com](https://render.com)

---

## 🌐 Frontend Deployment (Static Hosting)

The frontend is static files under [frontend/](frontend/). It reads runtime values from [frontend/env-config.js](frontend/env-config.js). Generate this file during deploy using your hosting provider's environment variables.

### Option 1: Netlify (Recommended)

1. Create a new site from your repository
2. Set the following environment variables in Netlify UI:
   - `API_BASE_URL` → your Cloud Run URL ending with `/api/v1`
   - `CALENDAR_NAME` → default display name (optional)
   - `TIMEZONE` → default timezone (optional)
3. Build settings:
   - Build command:
     ```bash
     bash -lc "echo // Auto-generated > frontend/env-config.js && \
     echo window.ENV_API_BASE_URL='\"$API_BASE_URL\"'; >> frontend/env-config.js && \
     echo window.ENV_CALENDAR_NAME='\"${CALENDAR_NAME:-My Timetable}\"'; >> frontend/env-config.js && \
     echo window.ENV_TIMEZONE='\"${TIMEZONE:-UTC}\"'; >> frontend/env-config.js"
     ```
   - Publish directory: `frontend`
4. Deploy and test the app. If you see CORS errors, update backend `CORS_ORIGINS` to include your Netlify domain.

Alternative (Netlify `netlify.toml`):
```toml
[build]
  publish = "frontend"
  command = "bash scripts/gen-env.sh"
```
And create `scripts/gen-env.sh` to write [frontend/env-config.js](frontend/env-config.js) using `$API_BASE_URL`, `$CALENDAR_NAME`, `$TIMEZONE`.

### Option 2: Vercel

1. Import the repository into Vercel
2. Under Project Settings → Environment Variables, add:
   - `API_BASE_URL`
   - `CALENDAR_NAME` (optional)
   - `TIMEZONE` (optional)
3. Build & Output Settings:
   - Build Command:
     ```bash
     bash -lc "echo // Auto-generated > frontend/env-config.js && \
     echo window.ENV_API_BASE_URL='\"$API_BASE_URL\"'; >> frontend/env-config.js && \
     echo window.ENV_CALENDAR_NAME='\"${CALENDAR_NAME:-My Timetable}\"'; >> frontend/env-config.js && \
     echo window.ENV_TIMEZONE='\"${TIMEZONE:-UTC}\"'; >> frontend/env-config.js"
     ```
   - Output Directory: `frontend`
4. Deploy. Ensure backend `CORS_ORIGINS` includes your Vercel domain.

### Option 3: GitHub Pages (Simple)

1. Build `env-config.js` locally:
   ```bash
   echo "window.ENV_API_BASE_URL='https://<cloud-run>/api/v1';" > frontend/env-config.js
   echo "window.ENV_CALENDAR_NAME='My Timetable';" >> frontend/env-config.js
   echo "window.ENV_TIMEZONE='UTC';" >> frontend/env-config.js
   ```
2. Push the `frontend/` folder to a `gh-pages` branch
3. Enable GitHub Pages in repo settings → Pages → Branch: `gh-pages`
4. Add your GitHub Pages URL to backend `CORS_ORIGINS`.

### Backend CORS Reminder

After deploying the frontend, update the backend CORS origins to include your frontend domain. Example:
```bash
gcloud run services update timetable-generator \
  --region us-central1 \
  --set-env-vars '^;^CORS_ORIGINS=["https://your-netlify-site.netlify.app","https://your-vercel-project.vercel.app"]'
```

### Quick Smoke Test

- Open the deployed frontend
- Upload a file or try a sample
- Confirm API calls succeed and no CORS errors appear in DevTools


2. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Name: `timetable-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add PostgreSQL**:
   - Click "New" → "PostgreSQL"
   - Copy the Internal Database URL

4. **Environment Variables**:
   ```
   DATABASE_URL=<postgres-url-from-step-3>
   PROJECT_NAME=Timetable Generator API
   API_V1_STR=/api/v1
   CORS_ORIGINS=["https://your-frontend.netlify.app"]
   TIMEZONE=UTC
   ```

5. **Deploy**: Click "Create Web Service"

### Option 3: AWS (Advanced)

#### Using AWS Elastic Beanstalk

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize**:
```bash
eb init -p python-3.11 timetable-api
```

3. **Create environment**:
```bash
eb create timetable-api-env
```

4. **Configure RDS**:
   - Add PostgreSQL database in EB console
   - Update DATABASE_URL environment variable

5. **Deploy**:
```bash
eb deploy
```

#### Using AWS Lambda + API Gateway (Serverless)

Use [Mangum](https://github.com/jordaneremieff/mangum):

```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

Deploy with AWS SAM or Serverless Framework.

---

## 🌐 Frontend Deployment

### Vercel (Recommended for React)

1. **Build frontend**:
```bash
npm run build
```

2. **Install Vercel CLI**:
```bash
npm i -g vercel
```

3. **Deploy**:
```bash
vercel
```

4. **Set API URL**:
   - In Vercel dashboard, set environment variable:
     ```
     REACT_APP_API_URL=https://your-api.railway.app
     ```

### Netlify (Recommended for Vue)

1. **Build frontend**:
```bash
npm run build
```

2. **Deploy via Netlify CLI**:
```bash
npm install -g netlify-cli
netlify deploy --prod
```

Or connect GitHub repository in Netlify dashboard.

---

## 🔐 Security Checklist

Before deploying to production:

- [ ] Change all default passwords
- [ ] Set strong `SECRET_KEY` in environment
- [ ] Enable HTTPS (most platforms do this automatically)
- [ ] Configure CORS properly (only allow your frontend domain)
- [ ] Set up rate limiting
- [ ] Enable database backups
- [ ] Set up monitoring (Sentry, Datadog, etc.)
- [ ] Review and limit file upload sizes
- [ ] Sanitize user inputs
- [ ] Use environment variables for all secrets

---

## 📊 Monitoring

### Add health check endpoint (already included)

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Railway Monitoring
- Built-in metrics dashboard
- CPU, Memory, Network usage
- Logs viewer

### Render Monitoring
- Metrics tab shows resource usage
- Log streaming available
- Set up alerts for errors

### External Monitoring
- [Sentry](https://sentry.io) for error tracking
- [Datadog](https://www.datadoghq.com) for APM
- [Uptime Robot](https://uptimerobot.com) for uptime monitoring

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v
      
      - name: Deploy to Railway
        run: |
          # Railway deploys automatically on push
          echo "Deployed!"
```

---

## 🗄️ Database Migration

For schema changes, use Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

---

## 🚀 Performance Optimization

### Production Settings

Update `.env`:
```env
# Use production database
DATABASE_URL=postgresql://user:pass@prod-db/dbname

# Increase workers
WORKERS=4

# Enable caching
REDIS_URL=redis://localhost:6379

# Set production CORS
CORS_ORIGINS=["https://yourdomain.com"]
```

### Add Gunicorn for production

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 📝 Deployment Checklist

- [ ] Tests pass locally
- [ ] Environment variables configured
- [ ] Database created and initialized
- [ ] CORS origins set correctly
- [ ] File upload limits configured
- [ ] Monitoring/logging set up
- [ ] Domain/SSL configured
- [ ] Backup strategy in place
- [ ] Documentation updated
- [ ] Team notified

---

## 🆘 Troubleshooting

### Database connection fails
- Check DATABASE_URL format
- Ensure database is running
- Verify network access/firewall rules

### File uploads fail
- Check MAX_UPLOAD_SIZE setting
- Verify uploads directory exists and is writable
- Check disk space

### Slow performance
- Add database indexes
- Enable caching (Redis)
- Increase worker count
- Use CDN for frontend

### CORS errors
- Verify CORS_ORIGINS includes frontend URL
- Check protocol (http vs https)
- Clear browser cache

---

**Deployment Complete!** 🎉

Your API should now be accessible at your deployment URL.
