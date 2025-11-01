"""Simplified unit tests for VideoRecording model."""
from datetime import datetime

import pytest
from sqlalchemy import select

from app.models import VideoRecording, Interview, Candidate


@pytest.mark.asyncio
async def test_create_video_recording(test_db):
    """Test creating a VideoRecording record."""
    # Create candidate
    candidate = Candidate(
        email="test@example.com",
        full_name="Test User",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    # Create interview
    interview = Interview(
        candidate_id=candidate.id,
        role_type="react"
    )
    test_db.add(interview)
    await test_db.flush()

    # Create video recording
    video = VideoRecording(
        interview_id=interview.id,
        storage_path="interviews/video_123.webm",
        file_size_bytes=1024000,
        duration_seconds=300,
        resolution="1280x720",
        bitrate_kbps=2500,
        codec="H.264"
    )
    test_db.add(video)
    await test_db.commit()

    # Verify
    assert video.id is not None
    assert video.interview_id == interview.id
    assert video.storage_path == "interviews/video_123.webm"
    assert video.file_size_bytes == 1024000
    assert video.duration_seconds == 300
    assert video.deleted_at is None
    assert video.upload_started_at is not None


@pytest.mark.asyncio
async def test_video_recording_jsonb_metadata(test_db):
    """Test JSONB recording_metadata field."""
    candidate = Candidate(
        email="test2@example.com",
        full_name="Test User 2",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="python"
    )
    test_db.add(interview)
    await test_db.flush()

    # Create video with metadata
    metadata = {
        "chunks_uploaded": 12,
        "total_chunks": 12,
        "camera_device": "FaceTime HD Camera"
    }
    video = VideoRecording(
        interview_id=interview.id,
        storage_path="interviews/video_789.webm",
        recording_metadata=metadata
    )
    test_db.add(video)
    await test_db.commit()

    # Verify metadata
    assert video.recording_metadata["chunks_uploaded"] == 12
    assert video.recording_metadata["camera_device"] == "FaceTime HD Camera"


@pytest.mark.asyncio
async def test_soft_delete_functionality(test_db):
    """Test soft delete with deleted_at timestamp."""
    candidate = Candidate(
        email="test3@example.com",
        full_name="Test User 3",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="javascript"
    )
    test_db.add(interview)
    await test_db.flush()

    video = VideoRecording(
        interview_id=interview.id,
        storage_path="interviews/video_to_delete.webm"
    )
    test_db.add(video)
    await test_db.flush()

    video_id = video.id
    assert video.deleted_at is None

    # Soft delete
    video.deleted_at = datetime.utcnow()
    await test_db.commit()

    # Verify soft delete
    result = await test_db.execute(
        select(VideoRecording).where(VideoRecording.id == video_id)
    )
    deleted_video = result.scalar_one()
    assert deleted_video.deleted_at is not None


@pytest.mark.asyncio
async def test_cascade_delete_with_interview(test_db):
    """Test that video is deleted when interview is deleted."""
    candidate = Candidate(
        email="test4@example.com",
        full_name="Test User 4",
        password_hash="hashed"
    )
    test_db.add(candidate)
    await test_db.flush()

    interview = Interview(
        candidate_id=candidate.id,
        role_type="fullstack"
    )
    test_db.add(interview)
    await test_db.flush()

    video = VideoRecording(
        interview_id=interview.id,
        storage_path="interviews/cascade_test.webm"
    )
    test_db.add(video)
    await test_db.flush()

    video_id = video.id

    # Delete interview
    await test_db.delete(interview)
    await test_db.commit()

    # Verify video was cascade deleted
    result = await test_db.execute(
        select(VideoRecording).where(VideoRecording.id == video_id)
    )
    deleted_video = result.scalar_one_or_none()
    assert deleted_video is None
