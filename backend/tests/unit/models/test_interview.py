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


@pytest.mark.asyncio
async def test_interview_tech_check_metadata(test_db):
    """Test tech_check_metadata JSONB field."""
    candidate = Candidate(
        email="techcheck@example.com",
        full_name="Tech Check Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    # Create interview with tech check metadata
    tech_check_data = {
        "audio": {
            "permission_granted": True,
            "test_passed": True,
            "audio_level_detected": 0.75,
            "test_timestamp": "2025-11-01T10:30:00Z"
        },
        "camera": {
            "permission_granted": True,
            "test_passed": True,
            "resolution": "1280x720",
            "test_timestamp": "2025-11-01T10:30:15Z"
        },
        "browser": "Chrome 119",
        "device_type": "desktop"
    }
    
    interview = Interview(
        candidate_id=candidate.id,
        role_type="react",
        status="scheduled",
        tech_check_metadata=tech_check_data
    )
    test_db.add(interview)
    await test_db.flush()
    await test_db.refresh(interview)

    # Verify JSONB data
    assert interview.tech_check_metadata is not None
    assert interview.tech_check_metadata["audio"]["test_passed"] is True
    assert interview.tech_check_metadata["camera"]["resolution"] == "1280x720"
    assert interview.tech_check_metadata["browser"] == "Chrome 119"


@pytest.mark.asyncio
async def test_interview_video_recording_consent(test_db):
    """Test video_recording_consent default value."""
    candidate = Candidate(
        email="consent@example.com",
        full_name="Consent Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    # Create interview without setting consent (should default to False)
    interview = Interview(
        candidate_id=candidate.id,
        role_type="python",
        status="scheduled"
    )
    test_db.add(interview)
    await test_db.flush()
    await test_db.refresh(interview)

    assert interview.video_recording_consent is False

    # Update consent
    interview.video_recording_consent = True
    await test_db.flush()
    await test_db.refresh(interview)

    assert interview.video_recording_consent is True


@pytest.mark.asyncio
async def test_interview_video_recording_status_enum(test_db):
    """Test video_recording_status enum values."""
    candidate = Candidate(
        email="videostatus@example.com",
        full_name="Video Status Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    # Test each valid enum value
    valid_statuses = ["not_recorded", "recording", "completed", "failed", "deleted"]
    
    for status in valid_statuses:
        interview = Interview(
            candidate_id=candidate.id,
            role_type="fullstack",
            status="scheduled",
            video_recording_status=status
        )
        test_db.add(interview)
        await test_db.flush()
        await test_db.refresh(interview)

        assert interview.video_recording_status == status
        
        # Clean up for next iteration
        await test_db.delete(interview)
        await test_db.flush()


@pytest.mark.asyncio
async def test_interview_video_recording_relationship(test_db):
    """Test relationship to VideoRecording model."""
    from app.models import VideoRecording
    
    candidate = Candidate(
        email="videorel@example.com",
        full_name="Video Relationship Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="react",
        status="in_progress",
        video_recording_consent=True,
        video_recording_status="recording"
    )
    test_db.add(interview)
    await test_db.flush()

    # Create video recording
    video = VideoRecording(
        interview_id=interview.id,
        storage_path="interviews/test_video.webm",
        file_size_bytes=1024000,
        duration_seconds=300
    )
    test_db.add(video)
    await test_db.flush()

    # Test relationship
    await test_db.refresh(interview, ["video_recording"])
    assert interview.video_recording is not None
    assert interview.video_recording.storage_path == "interviews/test_video.webm"
    assert interview.video_recording.duration_seconds == 300


@pytest.mark.asyncio
async def test_interview_video_recording_url(test_db):
    """Test video_recording_url field."""
    candidate = Candidate(
        email="videourl@example.com",
        full_name="Video URL Test",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="javascript",
        status="completed",
        video_recording_url="https://storage.supabase.co/interviews/video_123.webm"
    )
    test_db.add(interview)
    await test_db.flush()
    await test_db.refresh(interview)

    assert interview.video_recording_url is not None
    assert "supabase" in interview.video_recording_url
    assert interview.video_recording_url.endswith(".webm")
