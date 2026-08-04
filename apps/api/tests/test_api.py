"""
Tests for API endpoints - uses mocked Firebase
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Mock Firebase before importing app
with patch("firebase_admin.initialize_app"), \
     patch("firebase_admin.auth.verify_id_token", return_value={"uid": "test-user-123"}), \
     patch("firebase_admin.credentials.Certificate"):
    from main import app

client = TestClient(app)


@pytest.fixture
def auth_header():
    return {"Authorization": "Bearer test-token"}


def test_health_check():
    """Test the health check endpoint returns ok status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "Flourish API"


def test_root_endpoint():
    """Test the root endpoint returns welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["version"] == "1.0.0"
