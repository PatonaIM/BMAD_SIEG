"""Unit tests for VideoRecording model."""
import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoRecording, Interview, Candidate, Resume


@pytest.mark.asyncio
class TestVideoRecordingModel:
    """Test VideoRecording model functionality."""

    async def test_create_video_recording(self, test_db: AsyncSession):
        """Test creating a VideoRecording record."""
        # Create required parent records
        candidate = Candidate(
            email="test@example.com",
            full_name="Test User",
            password_hash="hashed"
        )
        test_db.add(candidate)
        await test_db.flush()

        resume = Resume(
            candidate_id=candidate.id,
            file_path="test.pdf",
            original_filename="resume.pdf"
        )
        test_db.add(resume)
        await test_db.flush()

        interview = Interview(
            candidate_id=candidate.id,
            resume_id=resume.id,
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
        assert video.resolution == "1280x720"
        assert video.bitrate_kbps == 2500
        assert video.codec == "H.264"
        assert video.deleted_at is None
        assert video.upload_started_at is not None
        assert video.upload_completed_at is None  # Not completed yet
        assert video.created_at is not None
        assert video.updated_at is not None

    async def test_video_recording_relationship(self, test_db: AsyncSession):
        """Test VideoRecording <-> Interview relationship."""
        # Create parent records
        candidate = Candidate(
            email="test2@example.com",
            full_name="Test User",
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

        # Create video recording
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/video_456.webm"
        )
        test_db.add(video)
        await test_db.commit()

        # Test relationship from interview side
        result = await test_db.execute(
            select(Interview).where(Interview.id == interview.id)
        )
        interview_from_db = result.scalar_one()
        assert interview_from_db.video_recording is not None
        assert interview_from_db.video_recording.id == video.id

        # Test relationship from video side
        result = await test_db.execute(
            select(VideoRecording).where(VideoRecording.id == video.id)
        )
        video_from_db = result.scalar_one()
        assert video_from_db.interview is not None
        assert video_from_db.interview.id == interview.id

    async def test_video_recording_jsonb_metadata(self, test_db: AsyncSession):
        """Test JSONB recording_metadata field."""
        # Create parent records
        candidate = Candidate(
            email="test3@example.com",
            full_name="Test User",
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

        # Create video with metadata
        metadata = {
            "chunks_uploaded": 12,
            "total_chunks": 12,
            "upload_errors": 0,
            "average_chunk_size_mb": 2.5,
            "encoding_preset": "web",
            "camera_device": "FaceTime HD Camera",
            "original_format": "video/webm"
        }
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/video_789.webm",
            recording_metadata=metadata
        )
        test_db.add(video)
        await test_db.commit()

        # Retrieve and verify
        result = await test_db.execute(
            select(VideoRecording).where(VideoRecording.id == video.id)
        )
        video_from_db = result.scalar_one()
        assert video_from_db.recording_metadata is not None
        assert video_from_db.recording_metadata["chunks_uploaded"] == 12
        assert video_from_db.recording_metadata["camera_device"] == "FaceTime HD Camera"
        assert video_from_db.recording_metadata["encoding_preset"] == "web"

    async def test_soft_delete_functionality(self, test_db: AsyncSession):
        """Test soft delete with deleted_at timestamp."""
        # Create parent records
        candidate = Candidate(
            email="test4@example.com",
            full_name="Test User",
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

        # Create video recording
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/video_to_delete.webm"
        )
        test_db.add(video)
        await test_db.commit()

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

        # Test filtering out deleted videos
        result = await test_db.execute(
            select(VideoRecording).where(
                VideoRecording.interview_id == interview.id,
                VideoRecording.deleted_at.is_(None)
            )
        )
        active_videos = result.scalars().all()
        assert len(active_videos) == 0

    async def test_upload_completion_tracking(self, test_db: AsyncSession):
        """Test upload_completed_at for tracking upload progress."""
        # Create parent records
        candidate = Candidate(
            email="test5@example.com",
            full_name="Test User",
            password_hash="hashed"
        )
        test_db.add(candidate)
        await test_db.flush()

        interview = Interview(
            candidate_id=candidate.id,
            role_type="react"
        )
        test_db.add(interview)
        await test_db.flush()

        # Create video with upload started
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/uploading_video.webm"
        )
        test_db.add(video)
        await test_db.commit()

        # Initially, upload not completed
        assert video.upload_completed_at is None

        # Mark upload as completed
        video.upload_completed_at = datetime.utcnow()
        await test_db.commit()

        # Verify
        result = await test_db.execute(
            select(VideoRecording).where(VideoRecording.id == video.id)
        )
        completed_video = result.scalar_one()
        assert completed_video.upload_completed_at is not None
        assert completed_video.upload_completed_at > completed_video.upload_started_at

    async def test_cascade_delete_with_interview(self, test_db: AsyncSession):
        """Test that video is deleted when interview is deleted (CASCADE)."""
        # Create parent records
        candidate = Candidate(
            email="test6@example.com",
            full_name="Test User",
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

        # Create video
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/cascade_test.webm"
        )
        test_db.add(video)
        await test_db.commit()

        video_id = video.id
        interview_id = interview.id

        # Delete interview
        await test_db.delete(interview)
        await test_db.commit()

        # Verify video was cascade deleted
        result = await test_db.execute(
            select(VideoRecording).where(VideoRecording.id == video_id)
        )
        deleted_video = result.scalar_one_or_none()
        assert deleted_video is None

    async def test_one_to_one_constraint(self, test_db: AsyncSession):
        """Test that one interview can only have one video recording."""
        # Create parent records
        candidate = Candidate(
            email="test7@example.com",
            full_name="Test User",
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

        # Create first video
        video1 = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/video_first.webm"
        )
        test_db.add(video1)
        await test_db.commit()

        # Try to create second video for same interview (should fail due to unique constraint)
        video2 = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/video_second.webm"
        )
        test_db.add(video2)
        
        with pytest.raises(Exception):  # Will raise IntegrityError
            await test_db.commit()

    async def test_video_recording_repr(self, test_db: AsyncSession):
        """Test __repr__ method."""
        # Create parent records
        candidate = Candidate(
            email="test8@example.com",
            full_name="Test User",
            password_hash="hashed"
        )
        test_db.add(candidate)
        await test_db.flush()

        interview = Interview(
            candidate_id=candidate.id,
            role_type="react"
        )
        test_db.add(interview)
        await test_db.flush()

        # Test uploading status
        video = VideoRecording(
            interview_id=interview.id,
            storage_path="interviews/repr_test.webm"
        )
        repr_str = repr(video)
        assert "VideoRecording" in repr_str
        assert "uploading" in repr_str

        # Test completed status
        video.upload_completed_at = datetime.utcnow()
        repr_str = repr(video)
        assert "completed" in repr_str

        # Test deleted status
        video.deleted_at = datetime.utcnow()
        repr_str = repr(video)
        assert "deleted" in repr_str
