"""
Application configuration settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "Timetable Generator API"
    API_V1_STR: str = "/api/v1"
    API_BASE_URL: str = "https://timetable-generator-183706276960.us-central1.run.app/api/v1"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Vue default
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./timetable_generator.db"
    # For PostgreSQL, use: "postgresql://user:password@localhost/dbname"
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"  # Fallback for local development
    ALLOWED_EXTENSIONS: set = {".pdf", ".xlsx", ".xls", ".csv"}
    
    # Google Cloud Storage settings
    GCP_PROJECT_ID: str = "timetable-calendar-app"
    GCS_BUCKET_NAME: str = "timetable-calendar-app-uploads"
    GCS_LOCATION: str = "us-central1"
    GCS_SIGNED_URL_EXPIRATION: int = 3600  # 1 hour in seconds
    USE_GCS: bool = True  # Set to False for local development
    
    # Calendar settings
    CALENDAR_NAME: str = "My Timetable"
    TIMEZONE: str = "UTC"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars not defined in model


settings = Settings()
