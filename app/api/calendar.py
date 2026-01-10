"""
Calendar generation endpoints
"""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import tempfile
from pathlib import Path

from app.schemas.event import (
    GenerateCalendarRequest,
    GenerateCalendarResponse,
    Event
)
from app.utils.calendar_generator import CalendarGenerator

router = APIRouter()


@router.post("/generate", response_model=GenerateCalendarResponse)
async def generate_calendar(request: GenerateCalendarRequest):
    """
    Generate an .ics calendar file from provided events
    """
    try:
        # Validate events before generating (matching parser strategy)
        validation_errors = []
        valid_events = []
        
        for i, event in enumerate(request.events):
            errors = []
            
            # Check required fields (matching parser: Day, Time, Course)
            if not event.date:
                errors.append("missing day/date")
            if not event.time:
                errors.append("missing time")
            if not event.title:
                errors.append("missing course/title")
            
            # Validate time format (must contain : for HH:MM format)
            # Parser normalizes to "HH:MM-HH:MM" or "HH:MM"
            if event.time:
                time_str = event.time.strip()
                if not (':' in time_str):
                    errors.append("invalid time format (expected HH:MM or HH:MM-HH:MM)")
                # Check if time has valid pattern
                elif not any(c.isdigit() for c in time_str):
                    errors.append("time must contain numbers")
            
            # Try to validate date can be parsed
            if event.date and not errors:
                try:
                    from dateutil import parser as date_parser
                    date_parser.parse(event.date, fuzzy=True)
                except:
                    errors.append("date format cannot be parsed")
            
            if errors:
                validation_errors.append({
                    "event_index": i + 1,
                    "title": event.title or "Untitled",
                    "date": event.date or "N/A",
                    "time": event.time or "N/A",
                    "errors": errors
                })
            else:
                valid_events.append(event)
        
        # If no valid events, return error with details
        if not valid_events:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "No valid events to generate calendar. All events failed validation.",
                    "validation_errors": validation_errors,
                    "hint": "Events must have Day, Time (HH:MM format), and Course filled."
                }
            )
        
        generator = CalendarGenerator()
        
        # Convert valid events to dict format
        events_data = [event.model_dump() for event in valid_events]
        
        # Generate calendar
        ics_content = generator.generate_ics(
            events=events_data,
            calendar_name=request.calendar_name,
            timezone=request.timezone
        )
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.ics',
            delete=False
        )
        temp_file.write(ics_content)
        temp_file.close()
        
        # Build response message
        message = f"Calendar generated with {len(valid_events)} events"
        if validation_errors:
            message += f" ({len(validation_errors)} events skipped due to validation errors)"
        
        return GenerateCalendarResponse(
            success=True,
            message=message,
            ics_url=f"/api/v1/calendar/download/{Path(temp_file.name).name}",
            event_count=len(valid_events)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating calendar: {str(e)}"
        )


@router.post("/download")
async def download_calendar(request: GenerateCalendarRequest):
    """
    Generate and directly download an .ics calendar file
    """
    try:
        generator = CalendarGenerator()
        
        # Convert request events to dict format
        events_data = [event.model_dump() for event in request.events]
        
        # Generate calendar
        ics_content = generator.generate_ics(
            events=events_data,
            calendar_name=request.calendar_name,
            timezone=request.timezone
        )
        
        # Return as downloadable file
        return Response(
            content=ics_content.encode('utf-8'),
            media_type="text/calendar",
            headers={
                "Content-Disposition": f"attachment; filename={request.calendar_name.replace(' ', '_')}.ics"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating calendar: {str(e)}"
        )


@router.post("/preview")
async def preview_calendar(request: GenerateCalendarRequest):
    """
    Preview calendar data without downloading
    """
    try:
        generator = CalendarGenerator()
        
        # Convert request events to dict format
        events_data = [event.model_dump() for event in request.events]
        
        # Generate summary
        summary = generator.generate_summary(
            events=events_data,
            calendar_name=request.calendar_name
        )
        
        return {
            "success": True,
            "calendar_name": request.calendar_name,
            "timezone": request.timezone,
            "event_count": len(events_data),
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error previewing calendar: {str(e)}"
        )
