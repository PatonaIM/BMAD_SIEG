"""Unit tests for security utilities."""
from datetime import timedelta

import pytest
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


def test_hash_password_creates_different_hashes():
    """Test that hashing same password twice produces different hashes."""
    password = "TestPassword123!"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2  # bcrypt uses random salt
    assert len(hash1) > 0
    assert len(hash2) > 0


def test_verify_password_with_correct_password():
    """Test password verification succeeds with correct password."""
    password = "TestPassword123!"
    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_verify_password_with_incorrect_password():
    """Test password verification fails with incorrect password."""
    password = "TestPassword123!"
    wrong_password = "WrongPassword456!"
    password_hash = hash_password(password)

    assert verify_password(wrong_password, password_hash) is False


def test_create_access_token_generates_valid_jwt():
    """Test JWT token creation."""
    from uuid import uuid4

    user_id = uuid4()
    token = create_access_token(user_id)

    # Verify token can be decoded
    payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm]
    )

    assert payload["sub"] == str(user_id)
    assert "exp" in payload


def test_create_access_token_with_custom_expiry():
    """Test JWT token creation with custom expiration."""
    from uuid import uuid4

    user_id = uuid4()
    expires_delta = timedelta(hours=1)
    token = create_access_token(user_id, expires_delta)

    payload = jwt.decode(
        token,
        settings.jwt_secret.get_secret_value(),
        algorithms=[settings.jwt_algorithm]
    )

    assert payload["sub"] == str(user_id)


def test_verify_token_with_valid_token():
    """Test token verification with valid token."""
    from uuid import uuid4

    user_id = uuid4()
    token = create_access_token(user_id)

    decoded_user_id = verify_token(token)

    assert decoded_user_id == user_id


def test_verify_token_with_invalid_token():
    """Test token verification fails with invalid token."""
    invalid_token = "invalid.token.here"

    with pytest.raises(JWTError):
        verify_token(invalid_token)


def test_verify_token_with_expired_token():
    """Test token verification fails with expired token."""
    from uuid import uuid4

    user_id = uuid4()
    # Create token that expires immediately
    token = create_access_token(user_id, timedelta(seconds=-1))

    with pytest.raises(JWTError):
        verify_token(token)


def test_verify_token_with_missing_subject():
    """Test token verification fails when subject is missing."""
    from datetime import datetime

    # Create token without 'sub' field
    token = jwt.encode(
        {"exp": datetime.utcnow().timestamp() + 3600},
        settings.jwt_secret.get_secret_value(),
        algorithm=settings.jwt_algorithm
    )

    with pytest.raises(JWTError):
        verify_token(token)
