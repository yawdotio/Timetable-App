"""
Configuration endpoint for frontend deployments
"""
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/config", tags=["Config"])
async def get_frontend_config():
    """Return runtime configuration for the frontend"""
    return {
        "api_base_url": settings.API_BASE_URL,
        "calendar_name": settings.CALENDAR_NAME,
        "timezone": settings.TIMEZONE,
        "max_upload_size": settings.MAX_UPLOAD_SIZE,
    }
