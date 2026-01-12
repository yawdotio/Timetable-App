# Google Cloud Storage Setup Guide

This guide explains how to configure Google Cloud Storage for the Timetable Generator application to persist uploaded files in a serverless/cloud environment.

## Overview

The application uses Google Cloud Storage (GCS) to store uploaded timetable files (CSV, Excel, PDF) instead of local disk storage, which is ephemeral in serverless environments like Cloud Run.

**Configuration:**
- **GCP Project:** `timetable-calendar-app`
- **Region:** `us-central1`
- **Bucket:** `timetable-calendar-app-uploads`
- **Access:** Private bucket with signed URLs for downloads
- **Files:** Stored with UUID prefix to avoid collisions

## Prerequisites

1. **Google Cloud Project**
   - Project ID: `timetable-calendar-app`
   - Billing must be enabled

2. **gcloud CLI** (for setup)
   ```bash
   # Install from: https://cloud.google.com/sdk/docs/install
   gcloud --version
   ```

## Setup Steps

### 1. Authenticate with Google Cloud

```bash
# Login to your Google account
gcloud auth login

# Set your project
gcloud config set project timetable-calendar-app

# Verify project
gcloud config get-value project
```

### 2. Enable Required APIs

```bash
# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Cloud Build (if using Cloud Run)
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

### 3. Create Storage Bucket

```bash
# Create the bucket in us-central1
gsutil mb -l us-central1 gs://timetable-calendar-app-uploads

# Verify bucket was created
gsutil ls

# Set uniform bucket-level access (recommended)
gsutil uniformbucketlevelaccess set on gs://timetable-calendar-app-uploads
```

**Note:** The bucket will also be auto-created by the application on first run if it doesn't exist.

### 4. Create Service Account

```bash
# Create service account for the application
gcloud iam service-accounts create timetable-storage-sa \
    --display-name="Timetable Storage Service Account" \
    --description="Service account for managing timetable file uploads"

# Grant Storage Object Admin permissions to the service account
gcloud projects add-iam-policy-binding timetable-calendar-app \
    --member="serviceAccount:timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### 5. Generate Service Account Key (for local development)

```bash
# Create and download key file
gcloud iam service-accounts keys create gcs-key.json \
    --iam-account=timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com

# Move to a secure location
mv gcs-key.json ~/.gcp/timetable-gcs-key.json
chmod 600 ~/.gcp/timetable-gcs-key.json
```

**⚠️ Security Warning:** Never commit this key file to version control!

### 6. Configure Application Environment

#### Local Development (.env file)

```bash
# Add to your .env file
USE_GCS=true
GCP_PROJECT_ID=timetable-calendar-app
GCS_BUCKET_NAME=timetable-calendar-app-uploads
GCS_LOCATION=us-central1
GCS_SIGNED_URL_EXPIRATION=3600
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcs-key.json
```

**Windows:**
```
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourUser\.gcp\timetable-gcs-key.json
```

**Linux/Mac:**
```
GOOGLE_APPLICATION_CREDENTIALS=/home/youruser/.gcp/timetable-gcs-key.json
```

#### Cloud Run Deployment

For Cloud Run, use Workload Identity instead of key files:

```bash
# Deploy with service account attached
gcloud run deploy timetable-generator \
    --image gcr.io/timetable-calendar-app/timetable-generator \
    --service-account=timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com \
    --region=us-central1 \
    --set-env-vars="USE_GCS=true,GCP_PROJECT_ID=timetable-calendar-app,GCS_BUCKET_NAME=timetable-calendar-app-uploads"
```

**No `GOOGLE_APPLICATION_CREDENTIALS` needed** - Cloud Run automatically uses the attached service account.

### 7. Test the Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --reload

# Test file upload via API or admin UI
# Files should now be stored in GCS bucket
```

Verify files are uploaded:
```bash
# List files in bucket
gsutil ls gs://timetable-calendar-app-uploads/

# View file details
gsutil ls -L gs://timetable-calendar-app-uploads/
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `USE_GCS` | No | `true` | Enable/disable GCS storage (use `false` for local dev) |
| `GCP_PROJECT_ID` | Yes | `timetable-calendar-app` | Google Cloud project ID |
| `GCS_BUCKET_NAME` | Yes | `timetable-calendar-app-uploads` | GCS bucket name |
| `GCS_LOCATION` | No | `us-central1` | Bucket region |
| `GCS_SIGNED_URL_EXPIRATION` | No | `3600` | Signed URL expiration (seconds) |
| `GOOGLE_APPLICATION_CREDENTIALS` | Local only | - | Path to service account key JSON |

### Storage Module Functions

The `app/utils/storage.py` module provides:

- `upload_file(content, filename, upload_id)` - Upload file to GCS
- `download_file(blob_name)` - Download file from GCS
- `delete_file(blob_name)` - Delete file from GCS
- `get_signed_url(blob_name, expiration)` - Generate temporary download URL
- `file_exists(blob_name)` - Check if file exists
- `list_files(prefix)` - List all files in bucket

## Bucket Lifecycle Management

### Auto-delete old files (optional)

To automatically delete files older than 90 days:

```bash
# Create lifecycle configuration
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {
          "type": "Delete"
        },
        "condition": {
          "age": 90
        }
      }
    ]
  }
}
EOF

# Apply lifecycle policy
gsutil lifecycle set lifecycle.json gs://timetable-calendar-app-uploads/
```

### Enable versioning (optional)

```bash
# Enable versioning to keep old versions of files
gsutil versioning set on gs://timetable-calendar-app-uploads/
```

## Security Best Practices

1. **Use Workload Identity** in production instead of service account keys
2. **Limit service account permissions** to only what's needed (Storage Object Admin)
3. **Never commit** `gcs-key.json` or credentials to version control
4. **Use signed URLs** for temporary public access instead of making bucket public
5. **Enable audit logging** for compliance:
   ```bash
   gcloud logging read "resource.type=gcs_bucket AND resource.labels.bucket_name=timetable-calendar-app-uploads"
   ```

## Cost Considerations

### Storage Pricing (us-central1, Standard Storage)
- Storage: ~$0.020/GB/month
- Class A operations (write): $0.05 per 10,000 operations
- Class B operations (read): $0.004 per 10,000 operations
- Network egress: First 1 GB free, then varies by region

### Example Monthly Cost
For 1,000 uploads/month (avg 2 MB each):
- Storage: 2 GB × $0.020 = $0.04
- Uploads: 1,000 operations × $0.05/10,000 = $0.005
- Downloads: 5,000 operations × $0.004/10,000 = $0.002
- **Total: ~$0.05/month**

## Troubleshooting

### Error: "Could not load the default credentials"

**Solution:**
```bash
# Set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcs-key.json"

# Or authenticate with application default credentials
gcloud auth application-default login
```

### Error: "Bucket not found"

**Solution:**
```bash
# Create the bucket manually
gsutil mb -l us-central1 gs://timetable-calendar-app-uploads

# Or let the app create it automatically (requires storage.buckets.create permission)
```

### Error: "Permission denied"

**Solution:**
```bash
# Verify service account has correct permissions
gcloud projects get-iam-policy timetable-calendar-app \
    --flatten="bindings[].members" \
    --filter="bindings.members:timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com"

# Add missing permission
gcloud projects add-iam-policy-binding timetable-calendar-app \
    --member="serviceAccount:timetable-storage-sa@timetable-calendar-app.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"
```

### Local Development Without GCS

To use local file storage during development:

```bash
# In .env file
USE_GCS=false
UPLOAD_DIR=uploads
```

Files will be stored in the local `uploads/` directory.

## Migration from Local Storage

If you have existing files in the `uploads/` directory:

```bash
# Upload all existing files to GCS
gsutil -m cp -r uploads/* gs://timetable-calendar-app-uploads/

# Verify upload
gsutil ls gs://timetable-calendar-app-uploads/
```

## Monitoring

### View bucket details
```bash
# Get bucket info
gsutil du -sh gs://timetable-calendar-app-uploads/

# List recent operations
gcloud logging read "resource.type=gcs_bucket" --limit 50 --format json
```

### Set up alerts (optional)
```bash
# Create alert for high storage usage
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="GCS High Storage" \
    --condition-threshold-value=10 \
    --condition-threshold-duration=60s
```

## Additional Resources

- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Python Client Library](https://googleapis.dev/python/storage/latest/index.html)
- [Best Practices](https://cloud.google.com/storage/docs/best-practices)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
