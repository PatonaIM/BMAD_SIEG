"""
Unit tests for health check endpoint
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 status code"""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_response_structure(client):
    """Test that health endpoint returns correct JSON structure"""
    response = client.get("/health")
    data = response.json()

    # Check that required fields exist
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data


def test_health_endpoint_status_value(client):
    """Test that health endpoint returns 'healthy' status"""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"


def test_health_endpoint_version_value(client):
    """Test that health endpoint returns correct version"""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == "1.0.0"


def test_health_endpoint_timestamp_format(client):
    """Test that health endpoint timestamp is in ISO format"""
    response = client.get("/health")
    data = response.json()

    # Check that timestamp ends with 'Z' (UTC timezone indicator)
    assert data["timestamp"].endswith("Z")

    # Check that timestamp can be parsed as ISO format
    from datetime import datetime

    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")
