# Multi-stage Docker build for Timetable Generator API

# Stage 1: Base
FROM python:3.11-slim as base

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy application code
COPY ./app ./app
COPY ./init_db.py .
COPY ./.env.example ./.env

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Initialize database and run application
CMD python init_db.py && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
