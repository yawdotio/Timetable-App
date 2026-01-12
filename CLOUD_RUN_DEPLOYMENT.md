# Cloud Run Deployment with GCS

Quick guide for deploying to Google Cloud Run with Cloud Storage enabled.

## Prerequisites

1. Complete GCS setup: Follow [GCS_SETUP.md](GCS_SETUP.md) steps 1-4
2. Docker installed locally (for building image)
3. Service account created: `timetable-storage-sa`

## Deployment Steps

### 1. Build and Push Container Image

```bash
# Set project
gcloud config set project timetable-calendar-app

# Enable Artifact Registry or Container Registry
gcloud services enable artifactregistry.googleapis.com

# Create artifact registry repository (first time only)
gcloud artifacts repositories create timetable-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Timetable Generator Docker images"

# Build and push image
gcloud builds submit --tag us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest

# Alternative: Build locally and push
docker build -t us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest .
docker push us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest
```

### 2. Deploy to Cloud Run with Workload Identity

```bash
# Deploy with service account (no key file needed!)
gcloud run deploy timetable-generator \
    --image us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest \
    --platform managed \
    --region us-central1 \
    --service-account timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars "USE_GCS=true,GCP_PROJECT_ID=timetable-calendar-app,GCS_BUCKET_NAME=timetable-calendar-app-uploads,GCS_LOCATION=us-central1,DATABASE_URL=sqlite:///./timetable_generator.db" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10
```

**Important Notes:**
- `--service-account` enables Workload Identity (no key file needed)
- No `GOOGLE_APPLICATION_CREDENTIALS` environment variable required
- Cloud Run automatically injects credentials for the service account

### 3. Verify Deployment

```bash
# Get service URL
gcloud run services describe timetable-generator --region us-central1 --format="value(status.url)"

# Test endpoint
curl https://timetable-generator-XXXXX.run.app/api/v1/config

# Check logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=timetable-generator" --limit 50
```

### 4. Update CORS for Frontend

If deploying frontend to Vercel/Netlify, update CORS:

```bash
# Redeploy with CORS origins
gcloud run deploy timetable-generator \
    --image us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest \
    --region us-central1 \
    --update-env-vars "CORS_ORIGINS=https://your-frontend.vercel.app,https://*.vercel.app"
```

## Using Cloud SQL (Optional)

For production database instead of SQLite:

```bash
# Create Cloud SQL instance
gcloud sql instances create timetable-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create timetable_generator --instance=timetable-db

# Set password for postgres user
gcloud sql users set-password postgres \
    --instance=timetable-db \
    --password=YOUR_SECURE_PASSWORD

# Deploy Cloud Run with Cloud SQL connection
gcloud run deploy timetable-generator \
    --image us-central1-docker.pkg.dev/timetable-calendar-app/timetable-repo/timetable-generator:latest \
    --region us-central1 \
    --add-cloudsql-instances timetable-calendar-app:us-central1:timetable-db \
    --set-env-vars "DATABASE_URL=postgresql://postgres:YOUR_SECURE_PASSWORD@/timetable_generator?host=/cloudsql/timetable-calendar-app:us-central1:timetable-db"
```

## Continuous Deployment with Cloud Build

Create `cloudbuild.yaml` (already exists):

```yaml
steps:
  # Build image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'us-central1-docker.pkg.dev/$PROJECT_ID/timetable-repo/timetable-generator:$COMMIT_SHA', '.']
  
  # Push image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'us-central1-docker.pkg.dev/$PROJECT_ID/timetable-repo/timetable-generator:$COMMIT_SHA']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'timetable-generator'
      - '--image=us-central1-docker.pkg.dev/$PROJECT_ID/timetable-repo/timetable-generator:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--service-account=timetable-storage-sa@$PROJECT_ID.iam.gserviceaccount.com'

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/timetable-repo/timetable-generator:$COMMIT_SHA'
```

Set up trigger:
```bash
gcloud builds triggers create github \
    --repo-name=timetable-generator \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Environment Variables Reference

| Variable | Value for Cloud Run |
|----------|---------------------|
| `USE_GCS` | `true` |
| `GCP_PROJECT_ID` | `timetable-calendar-app` |
| `GCS_BUCKET_NAME` | `timetable-calendar-app-uploads` |
| `GCS_LOCATION` | `us-central1` |
| `DATABASE_URL` | `sqlite:///./timetable_generator.db` (or Cloud SQL) |
| `CORS_ORIGINS` | Your frontend domains |
| `GOOGLE_APPLICATION_CREDENTIALS` | **NOT SET** (Workload Identity) |

## Troubleshooting

### Error: "Permission denied" when accessing GCS

Check service account is attached:
```bash
gcloud run services describe timetable-generator --region us-central1 --format="value(spec.template.spec.serviceAccountName)"
```

Verify IAM permissions:
```bash
gcloud projects get-iam-policy timetable-calendar-app \
    --flatten="bindings[].members" \
    --filter="bindings.members:timetable-storage-sa@"
```

### Error: "Could not load credentials"

Ensure `GOOGLE_APPLICATION_CREDENTIALS` is **not** set in Cloud Run environment variables.

### Service crashes on startup

Check logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 100 --format json
```

### Cannot create bucket

Grant bucket creation permission:
```bash
gcloud projects add-iam-policy-binding timetable-calendar-app \
    --member="serviceAccount:timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

## Cost Optimization

1. **Use minimum resources**: `--memory 512Mi --cpu 1`
2. **Set max instances**: `--max-instances 10`
3. **Enable request-based billing**: Automatically enabled for Cloud Run
4. **Use lifecycle policies**: Auto-delete old uploads after 90 days

Estimated monthly cost for moderate usage:
- Cloud Run: $0-5 (within free tier)
- Cloud Storage: $0.05 (see GCS_SETUP.md)
- Total: ~$5/month or less

## Monitoring

View metrics in Cloud Console:
- https://console.cloud.google.com/run/detail/us-central1/timetable-generator

Or via CLI:
```bash
# Request count
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_count"' \
    --format=json

# Latency
gcloud monitoring time-series list \
    --filter='metric.type="run.googleapis.com/request_latencies"' \
    --format=json
```
