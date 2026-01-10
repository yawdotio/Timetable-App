#!/usr/bin/env python3
"""
Database initialization script.
Creates all tables in the database using SQLAlchemy models.
Supports both local development and cloud deployments (Supabase, Cloud SQL, etc.)
"""
import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.core.database import Base  # Import SQLAlchemy Base where models are registered

# Load environment variables from .env file
load_dotenv()

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    # 1. Get the DB_URL from the environment (passed by Cloud Build)
    # Falls back to DATABASE_URL for compatibility
    database_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
    
    if not database_url:
        logger.error("DB_URL or DATABASE_URL environment variable is not set.")
        sys.exit(1)

    # 2. Fix for SQLAlchemy if the URL starts with "postgres://" (Supabase default)
    # SQLAlchemy requires "postgresql://"
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        logger.info("Converted postgres:// to postgresql:// for SQLAlchemy compatibility")

    try:
        # 3. Create the engine
        logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")
        engine = create_engine(database_url)
        
        # 4. Create all tables defined in your models
        # This function checks "IF NOT EXISTS" automatically
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
