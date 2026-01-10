"""
Upload endpoints for file processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasicCredentials
from sqlalchemy.orm import Session
from typing import List, Dict
import os
import uuid
import re
from pathlib import Path
from urllib.parse import urlparse, unquote
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import security, require_admin
from app.schemas.event import FileUploadResponse, FileUploadUrlRequest, ProcessingStatus
from app.models.subscription import UploadHistory, SavedUpload
from app.utils.parser import FileParser
from datetime import datetime

# In-memory storage for uploaded files (could be moved to Redis/database for production)
file_cache: Dict[str, str] = {}

router = APIRouter()


def _infer_extension(filename: str, content_type: str) -> str:
    """Infer file extension from filename or content type."""
    ext = Path(filename).suffix.lower()
    if ext:
        return ext
    if not content_type:
        return ""
    content_type = content_type.lower()
    if "pdf" in content_type:
        return ".pdf"
    if "csv" in content_type:
        return ".csv"
    if "excel" in content_type or "spreadsheetml" in content_type:
        return ".xlsx"
    return ""


def _transform_shared_link(url: str) -> str:
    """
    Detects Google/Microsoft viewer links and converts them to 
    direct download/export URLs.
    """
    # 1. Google Sheets -> Export as XLSX
    if "docs.google.com/spreadsheets" in url:
        return re.sub(r'/edit.*', '/export?format=xlsx', url)
    
    # 2. Google Docs -> Export as PDF (to fit your PDF parsing logic)
    elif "docs.google.com/document" in url:
        return re.sub(r'/edit.*', '/export?format=pdf', url)
    
    # 3. Microsoft OneDrive / SharePoint
    elif "sharepoint.com" in url or "onedrive.live.com" in url or "1drv.ms" in url:
        # If it's a specific OneDrive 'embed' or 'view' link, switch to download
        if "embed" in url or "view.aspx" in url:
            return url.replace("embed", "download").replace("view.aspx", "download")
        
        # Otherwise, force the generic download flag
        if "download=1" not in url:
            separator = "&" if "?" in url else "?"
            return f"{url}{separator}download=1"
            
    return url


def _get_filename_from_headers(response, url_path_filename: str) -> str:
    """
    Tries to extract the real filename from the Content-Disposition header.
    Falls back to the URL path if not found.
    """
    content_disposition = response.headers.get("content-disposition", "")
    if "filename=" in content_disposition:
        # Extract filename="example.xlsx" -> example.xlsx
        fname = re.findall(r'filename="?([^";\\/]+)"?', content_disposition)
        if fname:
            return unquote(fname[0])
            
    # Fallback to URL path, or a default generic name
    if not url_path_filename or url_path_filename == "export":
        # Guess based on content type if URL name is useless (like 'export')
        ct = response.headers.get("content-type", "")
        if "spreadsheet" in ct or "excel" in ct:
            return "downloaded_sheet.xlsx"
        elif "pdf" in ct:
            return "downloaded_doc.pdf"
        return "downloaded_file"
        
    return url_path_filename


@router.post("/file", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    sheet_name: str | None = Form(None),
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Upload a file (PDF, Excel, CSV) and extract preview data - Admin only
    """
    admin = require_admin(credentials)
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Generate unique upload ID
    upload_id = str(uuid.uuid4())
    
    # Save file
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / f"{upload_id}_{file.filename}"
    
    try:
        # Save uploaded file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create upload history record
        upload_record = UploadHistory(
            id=upload_id,
            filename=file.filename,
            file_type=file_ext,
            file_size=str(len(contents)),
            status="processing"
        )
        db.add(upload_record)
        db.commit()
        
        # Parse file
        parser = FileParser()
        parsed_data = parser.parse_file(str(file_path), file_ext, sheet_name=sheet_name)
        
        # Update status
        upload_record.status = "completed"
        upload_record.events_extracted = str(len(parsed_data.get("data", [])))
        upload_record.processed_at = datetime.utcnow()
        db.commit()
        
        # Cache the file path for re-parsing different sheets (optional)
        file_cache[upload_id] = str(file_path)
        
        return FileUploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            file_type=file_ext,
            status="success",
            preview_data=parsed_data.get("data", []),  # Return all rows
            detected_columns=parsed_data.get("columns", []),
            suggested_mapping=parsed_data.get("suggested_mapping", {}),
            sheet_used=parsed_data.get("sheet_used"),
            available_sheets=parsed_data.get("available_sheets", []),
            message=f"Successfully extracted {len(parsed_data.get('data', []))} rows"
        )
        
    except Exception as e:
        # Update error status
        if 'upload_record' in locals():
            upload_record.status = "failed"
            upload_record.error_message = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@router.post("/url", response_model=FileUploadResponse)
async def upload_from_url(
    payload: FileUploadUrlRequest,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Fetch a remote file by URL (handling Google/MS links) and extract preview data - Admin only.
    """
    admin = require_admin(credentials)
    # 1. Transform the URL (View -> Download)
    target_url = _transform_shared_link(str(payload.url))
    print("Transformed URL:", target_url)
    
    # Parse original path for fallback name
    parsed = urlparse(str(payload.url))
    url_filename = Path(parsed.path).name

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(target_url)
        except httpx.RequestError as e:
            raise HTTPException(status_code=400, detail=f"Failed to connect to URL: {str(e)}")

    if response.status_code >= 400:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch URL (status {response.status_code}). Ensure link is public."
        )

    # 2. Determine Filename (Headers > URL)
    # This is crucial for Google/MS links which often end in '/export' instead of '.xlsx'
    filename = _get_filename_from_headers(response, url_filename)

    # 3. Infer Extension & Validate
    file_ext = _infer_extension(filename, response.headers.get("content-type", ""))
    
    # Explicit check: If Google Sheet exported as .xlsx, treat as .xlsx
    if file_ext == "" and "xlsx" in target_url: 
        file_ext = ".xlsx"
    
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Detected: {file_ext}. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )

    # 4. Save & Process (Standard logic)
    upload_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Ensure filename has extension
    final_filename = filename if filename.endswith(file_ext) else filename + file_ext
    file_path = upload_dir / f"{upload_id}_{final_filename}"

    try:
        contents = response.content
        if not contents:
            raise HTTPException(status_code=400, detail="Fetched file is empty")

        with open(file_path, "wb") as f:
            f.write(contents)

        upload_record = UploadHistory(
            id=upload_id,
            filename=final_filename,
            file_type=file_ext,
            file_size=str(len(contents)),
            status="processing"
        )
        db.add(upload_record)
        db.commit()

        # 5. Parse
        parser = FileParser()
        parsed_data = parser.parse_file(str(file_path), file_ext, sheet_name=payload.sheet_name)

        upload_record.status = "completed"
        upload_record.events_extracted = str(len(parsed_data.get("data", [])))
        upload_record.processed_at = datetime.utcnow()
        db.commit()

        return FileUploadResponse(
            upload_id=upload_id,
            filename=final_filename,
            file_type=file_ext,
            status="success",
            preview_data=parsed_data.get("data", []),  # Return all rows
            detected_columns=parsed_data.get("columns", []),
            suggested_mapping=parsed_data.get("suggested_mapping", {}),
            sheet_used=parsed_data.get("sheet_used"),
            available_sheets=parsed_data.get("available_sheets", []),
            message=f"Successfully extracted {len(parsed_data.get('data', []))} rows"
        )

    except HTTPException:
        raise
    except Exception as e:
        if 'upload_record' in locals():
            upload_record.status = "failed"
            upload_record.error_message = str(e)
            db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Error processing file from URL: {str(e)}"
        )


@router.get("/status/{upload_id}", response_model=ProcessingStatus)
async def get_upload_status(
    upload_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the processing status of an uploaded file
    """
    upload = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return ProcessingStatus(
        upload_id=upload.id,
        status=upload.status,
        message=upload.error_message,
        events_extracted=int(upload.events_extracted) if upload.events_extracted else None
    )


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: str,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete an uploaded file and its record - Admin only
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


@router.post("/save")
async def save_upload_name(
    payload: dict,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Save a user-defined name for an uploaded file to reuse later - Admin only.
    Expects JSON: { "upload_id": "...", "name": "Fall Schedule" }
    """
    admin = require_admin(credentials)
    upload_id = str(payload.get("upload_id") or "").strip()
    name = str(payload.get("name") or "").strip()

    if not upload_id or not name:
        raise HTTPException(status_code=400, detail="upload_id and name are required")

    upload = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    saved = SavedUpload(
        upload_id=upload_id,
        name=name,
        filename=upload.filename,
        file_type=upload.file_type,
    )
    db.add(saved)
    db.commit()

    return {
        "id": saved.id,
        "upload_id": saved.upload_id,
        "name": saved.name,
        "filename": saved.filename,
        "file_type": saved.file_type,
        "created_at": str(saved.created_at) if saved.created_at else None,
    }


@router.get("/gallery")
async def list_saved_uploads(
    db: Session = Depends(get_db)
):
    """
    List saved uploads (gallery) with basic metadata.
    """
    items = db.query(SavedUpload).order_by(SavedUpload.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "upload_id": s.upload_id,
            "name": s.name,
            "filename": s.filename,
            "file_type": s.file_type,
            "created_at": str(s.created_at) if hasattr(s, 'created_at') and s.created_at else None,
        }
        for s in items
    ]


@router.post("/reparse/{upload_id}", response_model=FileUploadResponse)
async def reparse_file(
    upload_id: str,
    sheet_name: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Re-parse an already uploaded file with a different sheet name.
    Avoids re-uploading the file when the user selects a different sheet.
    """
    # Get the original upload record
    upload_record = db.query(UploadHistory).filter(UploadHistory.id == upload_id).first()
    if not upload_record:
        raise HTTPException(status_code=404, detail="Upload record not found")

    # Reconstruct the file path from upload directory and stored filename
    upload_dir = Path(settings.UPLOAD_DIR)
    file_path = upload_dir / f"{upload_id}_{upload_record.filename}"

    # Verify the file exists on disk
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found on server. Please re-upload the file."
        )

    try:
        # Re-parse with the new sheet name
        parser = FileParser()
        parsed_data = parser.parse_file(str(file_path), upload_record.file_type, sheet_name=sheet_name)

        # Update record
        upload_record.events_extracted = str(len(parsed_data.get("data", [])))
        upload_record.processed_at = datetime.utcnow()
        db.commit()

        return FileUploadResponse(
            upload_id=upload_id,
            filename=upload_record.filename,
            file_type=upload_record.file_type,
            status="success",
            preview_data=parsed_data.get("data", []),
            detected_columns=parsed_data.get("columns", []),
            suggested_mapping=parsed_data.get("suggested_mapping", {}),
            sheet_used=parsed_data.get("sheet_used"),
            available_sheets=parsed_data.get("available_sheets", []),
            message=f"Successfully extracted {len(parsed_data.get('data', []))} rows from sheet '{sheet_name or 'default'}'"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error re-parsing file: {str(e)}"
        )


@router.put("/rename/{upload_id}")
async def rename_upload(
    upload_id: str,
    new_name: str = Form(...),
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Rename a saved upload in the gallery to a new user-defined name - Admin only.
    """
    admin = require_admin(credentials)
    
    saved_upload = db.query(SavedUpload).filter(SavedUpload.id == upload_id).first()
    
    if not saved_upload:
        raise HTTPException(status_code=404, detail="Saved upload not found")
    
    # Update the name field
    saved_upload.name = new_name
    db.commit()
    
    return {"message": "Upload renamed successfully"}


@router.delete("/saved/{saved_id}")
async def delete_saved_upload(
    saved_id: str,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Delete a saved upload record (from the gallery), without affecting the original file - Admin only.
    """
    admin = require_admin(credentials)
    
    saved_upload = db.query(SavedUpload).filter(SavedUpload.id == saved_id).first()
    
    if not saved_upload:
        raise HTTPException(status_code=404, detail="Saved upload not found")
    
    # Delete record
    db.delete(saved_upload)
    db.commit()
    
    return {"message": "Saved upload deleted successfully"}
