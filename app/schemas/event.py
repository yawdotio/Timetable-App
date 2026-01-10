"""
Pydantic schemas for request/response validation
"""
from pydantic import AnyHttpUrl, BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# Event schemas
class EventBase(BaseModel):
    """Base schema for a calendar event"""
    date: str
    time: Optional[str] = None
    title: str
    location: Optional[str] = None
    description: Optional[str] = None
    end_time: Optional[str] = None
    recurring: Optional[str] = Field(default="none", description="Recurrence pattern: none, weekly, MONDAY-SUNDAY, or daily")
    reminder_minutes: Optional[int] = Field(default=45, description="Reminder time in minutes before event")

    @field_validator('recurring')
    @classmethod
    def validate_recurring(cls, v: Optional[str]) -> str:
        if v is None:
            return "none"
        
        valid_patterns = {
            "none", "weekly", "daily",
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"
        }
        
        if v not in valid_patterns:
            raise ValueError(f"Invalid recurrence pattern. Must be one of: {', '.join(sorted(valid_patterns))}")
        return v


class EventCreate(EventBase):
    """Schema for creating events"""
    pass


class Event(EventBase):
    """Schema for event response"""
    id: Optional[str] = None
    
    class Config:
        from_attributes = True


# File upload schemas
class FileUploadResponse(BaseModel):
    """Response after file upload"""
    upload_id: str
    filename: str
    file_type: str
    status: str
    preview_data: List[Dict[str, Any]]
    detected_columns: List[str]
    suggested_mapping: Dict[str, Optional[str]] = {}
    sheet_used: Optional[str] = None
    available_sheets: List[str] = []
    message: str


class FileUploadUrlRequest(BaseModel):
    """Request schema for URL-based uploads"""
    url: AnyHttpUrl
    sheet_name: Optional[str] = None


class ColumnMapping(BaseModel):
    """Schema for column mapping"""
    date_column: Optional[str] = None
    time_column: Optional[str] = None
    title_column: str
    location_column: Optional[str] = None
    description_column: Optional[str] = None
    end_time_column: Optional[str] = None


class GenerateCalendarRequest(BaseModel):
    """Request schema for calendar generation"""
    events: List[EventCreate]
    calendar_name: Optional[str] = "My Timetable"
    timezone: Optional[str] = "UTC"


class GenerateCalendarResponse(BaseModel):
    """Response schema for calendar generation"""
    success: bool
    message: str
    ics_url: Optional[str] = None
    event_count: int


# Subscription schemas
class SubscriptionBase(BaseModel):
    """Base schema for subscription"""
    name: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_type: str  # 'pdf', 'excel', 'csv'
    parsing_rules: Dict[str, Any]
    calendar_name: Optional[str] = "My Timetable"
    timezone: Optional[str] = "UTC"


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating subscription"""
    pass


class Subscription(SubscriptionBase):
    """Schema for subscription response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_fetched_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Response for listing subscriptions"""
    subscriptions: List[Subscription]
    total: int


# Processing schemas
class ProcessingStatus(BaseModel):
    """Schema for processing status"""
    upload_id: str
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None
    events_extracted: Optional[int] = None
