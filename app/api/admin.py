"""
Admin panel endpoints for managing calendars
"""
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import security, require_admin
from app.models.subscription import UploadHistory, SavedUpload
from pathlib import Path
from app.core.config import settings

router = APIRouter()


@router.post("/login")
async def admin_login(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Admin login endpoint - validates credentials and returns auth token.
    """
    admin = require_admin(credentials)
    return {
        "status": "success",
        "message": "Admin authenticated",
        "username": admin["username"],
        "is_admin": True
    }


@router.get("/uploads")
async def list_all_uploads(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    List all uploaded files (admin only).
    """
    try:
        admin = require_admin(credentials)
        
        uploads = db.query(UploadHistory).order_by(UploadHistory.uploaded_at.desc()).all()
        return [
            {
                "id": u.id,
                "filename": u.filename,
                "file_type": u.file_type,
                "file_size": u.file_size,
                "status": u.status,
                "events_extracted": u.events_extracted,
                # Keep created_at alias for backward compatibility
                "uploaded_at": str(u.uploaded_at) if u.uploaded_at else None,
                "created_at": str(u.uploaded_at) if u.uploaded_at else None,
                "processed_at": str(u.processed_at) if u.processed_at else None,
            }
            for u in uploads
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error listing uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing uploads: {str(e)}")


@router.get("/saved-calendars")
async def list_all_saved_calendars(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    List all saved calendars (admin only).
    """
    try:
        admin = require_admin(credentials)
        
        saved = db.query(SavedUpload).order_by(SavedUpload.created_at.desc()).all()
        return [
            {
                "id": s.id,
                "upload_id": s.upload_id,
                "name": s.name,
                "filename": s.filename,
                "file_type": s.file_type,
                "created_at": str(s.created_at) if s.created_at else None,
            }
            for s in saved
        ]
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error listing saved calendars: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing calendars: {str(e)}")


@router.delete("/upload/{upload_id}")
async def delete_upload_admin(
    upload_id: str,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file (admin only).
    """
    admin = require_admin(credentials)
    
    upload = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Delete file
    upload_dir = Path(settings.UPLOAD_DIR)
    file_path = upload_dir / f"{upload_id}_{upload.filename}"
    if file_path.exists():
        file_path.unlink()
    
    # Delete record
    db.delete(upload)
    db.commit()
    
    return {"message": "Upload deleted successfully"}


@router.delete("/saved-calendar/{saved_id}")
async def delete_saved_calendar_admin(
    saved_id: str,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete a saved calendar (admin only).
    """
    admin = require_admin(credentials)
    
    saved = db.query(SavedUpload).filter(SavedUpload.id == saved_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved calendar not found")
    
    db.delete(saved)
    db.commit()
    
    return {"message": "Saved calendar deleted successfully"}


@router.put("/saved-calendar/{saved_id}")
async def rename_saved_calendar_admin(
    saved_id: str,
    new_name: str = Form(...),
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Rename a saved calendar (admin only).
    """
    admin = require_admin(credentials)
    
    saved = db.query(SavedUpload).filter(SavedUpload.id == saved_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved calendar not found")
    
    saved.name = new_name
    db.commit()
    
    return {"message": "Calendar renamed successfully"}
