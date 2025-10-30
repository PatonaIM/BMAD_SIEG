"""Integration tests for authentication endpoints."""
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_register_with_valid_data(test_client: AsyncClient):
    """Test registration endpoint with valid data."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "SecurePass123!",
            "phone": "+1234567890"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "candidate_id" in data


@pytest.mark.asyncio
async def test_register_with_duplicate_email(test_client: AsyncClient, test_candidate):
    """Test registration fails with duplicate email."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_candidate.email,
            "full_name": "Duplicate User",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_with_invalid_email(test_client: AsyncClient):
    """Test registration fails with invalid email format."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "full_name": "Test User",
            "password": "SecurePass123!"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_with_short_password(test_client: AsyncClient):
    """Test registration fails with password less than 8 characters."""
    response = await test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "full_name": "Test User",
            "password": "short"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_with_valid_credentials(test_client: AsyncClient, test_candidate):
    """Test login endpoint with valid credentials."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_candidate.email,
            "password": test_candidate._test_password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["email"] == test_candidate.email
    assert data["candidate_id"] == str(test_candidate.id)


@pytest.mark.asyncio
async def test_login_with_invalid_password(test_client: AsyncClient, test_candidate):
    """Test login fails with incorrect password."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_candidate.email,
            "password": "WrongPassword!"
        }
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_with_nonexistent_email(test_client: AsyncClient):
    """Test login fails with non-existent email."""
    response = await test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        }
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_start_interview_with_valid_token(test_client: AsyncClient, test_candidate):
    """Test starting interview with valid authentication token."""
    token = create_access_token(test_candidate.id)

    response = await test_client.post(
        "/api/v1/interviews/start",
        json={
            "role_type": "fullstack",
            "resume_id": None
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["candidate_id"] == str(test_candidate.id)
    assert data["role_type"] == "fullstack"
    assert data["status"] == "scheduled"
    assert "id" in data


@pytest.mark.asyncio
async def test_start_interview_without_token(test_client: AsyncClient):
    """Test starting interview without authentication token."""
    response = await test_client.post(
        "/api/v1/interviews/start",
        json={
            "role_type": "python"
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_interview_with_invalid_token(test_client: AsyncClient):
    """Test starting interview with invalid token."""
    response = await test_client.post(
        "/api/v1/interviews/start",
        json={
            "role_type": "react"
        },
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_start_interview_with_invalid_role_type(test_client: AsyncClient, test_candidate):
    """Test starting interview with invalid role_type."""
    token = create_access_token(test_candidate.id)

    response = await test_client.post(
        "/api/v1/interviews/start",
        json={
            "role_type": "invalid_role"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422  # Validation error
