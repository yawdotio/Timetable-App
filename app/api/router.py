"""
API Router - combines all endpoint routers
"""
from fastapi import APIRouter
from app.api import upload, calendar, subscription, admin

router = APIRouter()

# Include all sub-routers
router.include_router(upload.router, prefix="/upload", tags=["Upload"])
router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
router.include_router(subscription.router, prefix="/subscription", tags=["Subscription"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
