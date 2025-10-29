"""Unit tests for Interview model."""
from datetime import datetime
from uuid import UUID

import pytest

from app.models.candidate import Candidate
from app.models.interview import Interview


@pytest.mark.asyncio
async def test_interview_creation(test_db):
    """Test creating a new interview."""
    # Create candidate first
    candidate = Candidate(
        email="interview@example.com",
        full_name="Interview Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()
    await test_db.refresh(candidate)

    # Create interview
    interview = Interview(
        candidate_id=candidate.id,
        role_type="fullstack",
        status="scheduled"
    )

    test_db.add(interview)
    await test_db.flush()
    await test_db.refresh(interview)

    assert interview.id is not None
    assert isinstance(interview.id, UUID)
    assert interview.candidate_id == candidate.id
    assert interview.role_type == "fullstack"
    assert interview.status == "scheduled"
    assert interview.total_tokens_used == 0
    assert interview.cost_usd == 0.0


@pytest.mark.asyncio
async def test_interview_with_relationships(test_db):
    """Test interview with candidate relationship."""
    candidate = Candidate(
        email="relationships@example.com",
        full_name="Relationships Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="python",
        status="in_progress"
    )
    test_db.add(interview)
    await test_db.flush()

    # Access relationship
    await test_db.refresh(interview, ["candidate"])
    assert interview.candidate.email == "relationships@example.com"


@pytest.mark.asyncio
async def test_interview_status_transitions(test_db):
    """Test interview status changes."""
    candidate = Candidate(
        email="status@example.com",
        full_name="Status Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="react",
        status="scheduled"
    )
    test_db.add(interview)
    await test_db.flush()
    await test_db.refresh(interview)

    # Update status
    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    await test_db.flush()
    await test_db.refresh(interview)

    assert interview.status == "in_progress"
    assert interview.started_at is not None
