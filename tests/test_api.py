"""
Test API endpoints
"""
import pytest
from io import BytesIO


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_invalid_file(client):
    """Test uploading invalid file type"""
    file_content = b"test content"
    files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}
    
    response = client.post("/api/v1/upload/file", files=files)
    assert response.status_code == 400


def test_calendar_generation(client):
    """Test calendar generation"""
    events = [
        {
            "date": "2026-01-15",
            "time": "09:00",
            "title": "Test Event",
            "location": "Room 101"
        }
    ]
    
    response = client.post(
        "/api/v1/calendar/preview",
        json={
            "events": events,
            "calendar_name": "Test Calendar",
            "timezone": "UTC"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["event_count"] == 1
