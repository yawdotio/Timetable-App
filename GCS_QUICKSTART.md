# Quick Start: GCS Setup

Fast track to get GCS working for your timetable generator.

## Local Development (No GCS)

```bash
# 1. Update .env
echo "USE_GCS=false" >> .env

# 2. Install and run
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Done! Files saved to local `uploads/` folder.

---

## Local Development (With GCS)

```bash
# 1. Install gcloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Login and set project
gcloud auth login
gcloud config set project timetable-calendar-app

# 3. Enable APIs
gcloud services enable storage.googleapis.com

# 4. Create service account
gcloud iam service-accounts create timetable-storage-sa \
    --display-name="Timetable Storage"

# 5. Grant permissions
gcloud projects add-iam-policy-binding timetable-calendar-app \
    --member="serviceAccount:timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# 6. Create and download key
gcloud iam service-accounts keys create gcs-key.json \
    --iam-account=timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com

# 7. Set environment variable
# Windows:
set GOOGLE_APPLICATION_CREDENTIALS=%CD%\gcs-key.json

# Linux/Mac:
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/gcs-key.json"

# 8. Update .env
echo "USE_GCS=true" >> .env
echo "GCP_PROJECT_ID=timetable-calendar-app" >> .env
echo "GCS_BUCKET_NAME=timetable-calendar-app-uploads" >> .env
echo "GOOGLE_APPLICATION_CREDENTIALS=./gcs-key.json" >> .env

# 9. Install and run
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Bucket auto-creates on first upload!

---

## Cloud Run Deployment

```bash
# 1. Build and push image
gcloud builds submit --tag gcr.io/timetable-calendar-app/timetable-generator

# 2. Deploy
gcloud run deploy timetable-generator \
    --image gcr.io/timetable-calendar-app/timetable-generator \
    --platform managed \
    --region us-central1 \
    --service-account timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars "USE_GCS=true,GCP_PROJECT_ID=timetable-calendar-app,GCS_BUCKET_NAME=timetable-calendar-app-uploads"

# 3. Get URL
gcloud run services describe timetable-generator \
    --region us-central1 \
    --format="value(status.url)"
```

No key file needed - uses Workload Identity!

---

## Verify It's Working

```bash
# Check bucket exists
gsutil ls gs://timetable-calendar-app-uploads/

# Upload test file via curl
curl -X POST http://localhost:8000/api/v1/upload/file \
  -F "file=@sample_timetable.csv"

# Check file was uploaded to GCS
gsutil ls gs://timetable-calendar-app-uploads/
```

---

## Troubleshooting

### "Could not load credentials"
```bash
# Set the path
export GOOGLE_APPLICATION_CREDENTIALS="/full/path/to/gcs-key.json"
```

### "Permission denied"
```bash
# Verify role
gcloud projects get-iam-policy timetable-calendar-app \
    --flatten="bindings[].members" \
    --filter="bindings.members:timetable-storage-sa"
```

### "Import error: google.cloud"
```bash
pip install google-cloud-storage
```

---

## Need More Details?

- **Full setup**: See [GCS_SETUP.md](GCS_SETUP.md)
- **Deployment**: See [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md)
- **Summary**: See [GCS_INTEGRATION_SUMMARY.md](GCS_INTEGRATION_SUMMARY.md)

---

## Cost

Expected: **$0.05/month** (likely free tier)

---

## Security Checklist

- [ ] Service account has minimal permissions (Storage Object Admin)
- [ ] Key file (`gcs-key.json`) added to `.gitignore`
- [ ] Key file not committed to git
- [ ] Bucket is private (not public)
- [ ] Signed URLs used for temporary access

---

**That's it! Your uploads now persist in the cloud.** 🎉
