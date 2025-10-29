"""Unit tests for Candidate model."""
from datetime import datetime
from uuid import UUID

import pytest

from app.models.candidate import Candidate


@pytest.mark.asyncio
async def test_candidate_creation(test_db):
    """Test creating a new candidate."""
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed_password_123",
        phone="+1234567890"
    )

    test_db.add(candidate)
    await test_db.flush()
    await test_db.refresh(candidate)

    assert candidate.id is not None
    assert isinstance(candidate.id, UUID)
    assert candidate.email == "test@example.com"
    assert candidate.full_name == "Test User"
    assert candidate.status == "active"
    assert isinstance(candidate.created_at, datetime)
    assert isinstance(candidate.updated_at, datetime)


@pytest.mark.asyncio
async def test_candidate_default_values(test_db):
    """Test candidate default values."""
    candidate = Candidate(
        email="defaults@example.com",
        full_name="Defaults Test",
        password_hash="hashed_password"
    )

    test_db.add(candidate)
    await test_db.flush()
    await test_db.refresh(candidate)

    assert candidate.status == "active"
    assert candidate.phone is None
    assert candidate.created_at is not None
    assert candidate.updated_at is not None


@pytest.mark.asyncio
async def test_candidate_repr(test_db):
    """Test candidate string representation."""
    candidate = Candidate(
        email="repr@example.com",
        full_name="Repr Test",
        password_hash="hashed"
    )

    test_db.add(candidate)
    await test_db.flush()

    repr_str = repr(candidate)
    assert "Candidate" in repr_str
    assert "repr@example.com" in repr_str
