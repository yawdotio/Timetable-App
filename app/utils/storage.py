"""
Google Cloud Storage utilities for file persistence
"""
from google.cloud import storage
from google.cloud.exceptions import NotFound, GoogleCloudError
from pathlib import Path
from datetime import timedelta
from typing import Optional
import uuid
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GCSStorage:
    """Google Cloud Storage manager for upload files"""
    
    def __init__(self):
        """Initialize GCS client and bucket"""
        self.client = storage.Client(project=settings.GCP_PROJECT_ID)
        self.bucket_name = settings.GCS_BUCKET_NAME
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            self.bucket = self.client.get_bucket(self.bucket_name)
            logger.info(f"Connected to GCS bucket: {self.bucket_name}")
        except NotFound:
            # Create bucket if it doesn't exist
            logger.info(f"Creating GCS bucket: {self.bucket_name}")
            self.bucket = self.client.create_bucket(
                self.bucket_name,
                location=settings.GCS_LOCATION
            )
            logger.info(f"Created GCS bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to access/create GCS bucket: {e}")
            raise
    
    def upload_file(
        self, 
        file_content: bytes, 
        filename: str, 
        upload_id: Optional[str] = None
    ) -> str:
        """
        Upload file to GCS and return the blob name.
        
        Args:
            file_content: File bytes to upload
            filename: Original filename
            upload_id: Optional upload ID (generates new UUID if not provided)
        
        Returns:
            The blob name (object path) in GCS
        """
        if not upload_id:
            upload_id = str(uuid.uuid4())
        
        # Create blob name with UUID prefix to avoid collisions
        blob_name = f"{upload_id}_{filename}"
        
        try:
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(
                file_content,
                content_type=self._get_content_type(filename)
            )
            logger.info(f"Uploaded file to GCS: {blob_name}")
            return blob_name
        except GoogleCloudError as e:
            logger.error(f"Failed to upload to GCS: {e}")
            raise Exception(f"GCS upload failed: {str(e)}")
    
    def download_file(self, blob_name: str) -> bytes:
        """
        Download file content from GCS.
        
        Args:
            blob_name: The object path in GCS
        
        Returns:
            File content as bytes
        """
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                raise FileNotFoundError(f"File not found in GCS: {blob_name}")
            
            content = blob.download_as_bytes()
            logger.info(f"Downloaded file from GCS: {blob_name}")
            return content
        except GoogleCloudError as e:
            logger.error(f"Failed to download from GCS: {e}")
            raise Exception(f"GCS download failed: {str(e)}")
    
    def delete_file(self, blob_name: str) -> bool:
        """
        Delete file from GCS.
        
        Args:
            blob_name: The object path in GCS
        
        Returns:
            True if deleted successfully
        """
        try:
            blob = self.bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                logger.info(f"Deleted file from GCS: {blob_name}")
                return True
            else:
                logger.warning(f"File not found for deletion: {blob_name}")
                return False
        except GoogleCloudError as e:
            logger.error(f"Failed to delete from GCS: {e}")
            raise Exception(f"GCS deletion failed: {str(e)}")
    
    def get_signed_url(
        self, 
        blob_name: str, 
        expiration: int = 3600
    ) -> str:
        """
        Generate a signed URL for temporary public access.
        
        Args:
            blob_name: The object path in GCS
            expiration: URL expiration in seconds (default: 1 hour)
        
        Returns:
            Signed URL string
        """
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                raise FileNotFoundError(f"File not found in GCS: {blob_name}")
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(seconds=expiration),
                method="GET"
            )
            logger.info(f"Generated signed URL for: {blob_name}")
            return url
        except GoogleCloudError as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise Exception(f"Signed URL generation failed: {str(e)}")
    
    def file_exists(self, blob_name: str) -> bool:
        """
        Check if file exists in GCS.
        
        Args:
            blob_name: The object path in GCS
        
        Returns:
            True if file exists
        """
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except Exception as e:
            logger.error(f"Failed to check file existence: {e}")
            return False
    
    def list_files(self, prefix: Optional[str] = None) -> list:
        """
        List all files in the bucket (optionally filtered by prefix).
        
        Args:
            prefix: Optional prefix to filter results
        
        Returns:
            List of blob names
        """
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
            return [blob.name for blob in blobs]
        except GoogleCloudError as e:
            logger.error(f"Failed to list files: {e}")
            raise Exception(f"GCS list failed: {str(e)}")
    
    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Determine content type from file extension"""
        ext = Path(filename).suffix.lower()
        content_types = {
            ".pdf": "application/pdf",
            ".csv": "text/csv",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel"
        }
        return content_types.get(ext, "application/octet-stream")


# Singleton instance
_storage_instance: Optional[GCSStorage] = None


def get_storage() -> GCSStorage:
    """Get or create GCS storage singleton instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = GCSStorage()
    return _storage_instance
