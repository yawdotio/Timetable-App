"""
Database models for timetable subscriptions
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
import uuid
from app.core.database import Base


class Subscription(Base):
    """Model for dynamic calendar subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Subscription metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Source information
    source_url = Column(String, nullable=True)  # URL to fetch spreadsheet
    source_type = Column(String, nullable=False)  # 'pdf', 'excel', 'csv'
    
    # Parsing configuration (JSON)
    parsing_rules = Column(JSON, nullable=False)
    # Example: {
    #   "date_column": "Date",
    #   "time_column": "Time",
    #   "title_column": "Event",
    #   "location_column": "Location",
    #   "date_format": "DD/MM/YYYY"
    # }
    
    # Calendar settings
    calendar_name = Column(String, default="My Timetable")
    timezone = Column(String, default="UTC")
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Subscription {self.name} ({self.id})>"


class UploadHistory(Base):
    """Model for tracking file uploads"""
    __tablename__ = "upload_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # File information
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(String, nullable=False)
    
    # Processing status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Extracted data count
    events_extracted = Column(String, default="0")
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UploadHistory {self.filename} ({self.status})>"


class SavedUpload(Base):
    """Model for user-named saved uploads for reuse"""
    __tablename__ = "saved_uploads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String, nullable=False)  # references UploadHistory.id
    name = Column(String, nullable=False)

    # Optional metadata for quick display
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SavedUpload {self.name} ({self.upload_id})>"
