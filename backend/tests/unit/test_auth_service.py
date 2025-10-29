"""Unit tests for AuthService."""
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.candidate import Candidate
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_candidate_success():
    """Test successful candidate registration."""
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_email = AsyncMock(return_value=None)
    mock_repo.create = AsyncMock()

    auth_service = AuthService(mock_repo)

    email = "test@example.com"
    password = "TestPassword123!"
    full_name = "Test User"

    # Mock create to return a candidate
    def mock_create_side_effect(candidate):
        return candidate

    mock_repo.create.side_effect = mock_create_side_effect

    # Act
    candidate, token = await auth_service.register_candidate(email, password, full_name)

    # Assert
    assert candidate.email == email
    assert candidate.full_name == full_name
    assert candidate.status == "active"
    assert len(token) > 0
    mock_repo.get_by_email.assert_called_once_with(email)
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_register_candidate_duplicate_email():
    """Test registration fails with duplicate email."""
    # Arrange
    mock_repo = Mock()
    existing_candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Existing User",
        password_hash="hashed",
        status="active"
    )
    mock_repo.get_by_email = AsyncMock(return_value=existing_candidate)

    auth_service = AuthService(mock_repo)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_candidate(
            "test@example.com",
            "password",
            "Test User"
        )

    assert exc_info.value.status_code == 400
    assert "already registered" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_candidate_success():
    """Test successful candidate login."""
    # Arrange
    mock_repo = Mock()
    password = "TestPassword123!"
    password_hash = hash_password(password)

    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash=password_hash,
        status="active"
    )

    mock_repo.get_by_email = AsyncMock(return_value=candidate)
    auth_service = AuthService(mock_repo)

    # Act
    result_candidate, token = await auth_service.login_candidate(
        "test@example.com",
        password
    )

    # Assert
    assert result_candidate.id == candidate.id
    assert result_candidate.email == candidate.email
    assert len(token) > 0
    mock_repo.get_by_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_login_candidate_invalid_email():
    """Test login fails with non-existent email."""
    # Arrange
    mock_repo = Mock()
    mock_repo.get_by_email = AsyncMock(return_value=None)

    auth_service = AuthService(mock_repo)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_candidate(
            "nonexistent@example.com",
            "password"
        )

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_candidate_invalid_password():
    """Test login fails with incorrect password."""
    # Arrange
    mock_repo = Mock()
    password = "TestPassword123!"
    password_hash = hash_password(password)

    candidate = Candidate(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        password_hash=password_hash,
        status="active"
    )

    mock_repo.get_by_email = AsyncMock(return_value=candidate)
    auth_service = AuthService(mock_repo)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await auth_service.login_candidate(
            "test@example.com",
            "WrongPassword!"
        )

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in exc_info.value.detail
