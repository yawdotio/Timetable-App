"""
Authentication and authorization utilities for admin access
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os

security = HTTPBasic()

# Simple admin credentials (in production, use proper password hashing and database)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


def verify_admin_credentials(credentials: HTTPBasicCredentials) -> bool:
    """
    Verify admin credentials using HTTP Basic Auth.
    In production, use proper password hashing and database lookup.
    """
    return (
        credentials.username == ADMIN_USERNAME
        and credentials.password == ADMIN_PASSWORD
    )


def require_admin(credentials: HTTPBasicCredentials) -> dict:
    """
    Dependency for FastAPI routes that require admin authentication.
    Returns admin user info if credentials are valid.
    """
    if not verify_admin_credentials(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": credentials.username, "is_admin": True}
