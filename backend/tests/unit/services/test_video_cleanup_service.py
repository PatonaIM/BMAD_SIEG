"""Unit tests for VideoCleanupService."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, MagicMock
from uuid import uuid4

from app.models import VideoRecording
from app.services.video_cleanup_service import VideoCleanupService


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.add = Mock()
    session.delete = AsyncMock()
    return session


@pytest.fixture
def mock_storage_client():
    """Mock Supabase Storage client."""
    client = Mock()
    client.delete_video = AsyncMock(return_value=True)
    client.get_bucket_usage = AsyncMock(return_value={
        "total_size_bytes": 1000000,
        "total_size_gb": 0.001,
        "file_count": 10
    })
    return client


@pytest.fixture
def cleanup_service(mock_db_session, mock_storage_client):
    """Create VideoCleanupService instance with mocks."""
    return VideoCleanupService(mock_db_session, mock_storage_client)


@pytest.mark.asyncio
async def test_cleanup_expired_videos_success(cleanup_service, mock_db_session):
    """Test successful soft deletion of expired videos."""
    # Arrange
    expired_video = VideoRecording(
        id=uuid4(),
        interview_id=uuid4(),
        storage_path="org_123/interview_456/recording.mp4",
        file_size_bytes=10_000_000,
        duration_seconds=600,
        upload_completed_at=datetime.utcnow() - timedelta(days=35)
    )
    
    # Mock _get_expired_videos to return expired video
    cleanup_service._get_expired_videos = AsyncMock(return_value=[expired_video])
    
    # Act
    result = await cleanup_service.cleanup_expired_videos(retention_days=30)
    
    # Assert
    assert result["soft_deleted"] == 1
    assert result["errors"] == 0
    assert expired_video.deleted_at is not None
    mock_db_session.add.assert_called_once_with(expired_video)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_videos_no_videos(cleanup_service, mock_db_session):
    """Test cleanup when no expired videos exist."""
    # Arrange
    cleanup_service._get_expired_videos = AsyncMock(return_value=[])
    
    # Act
    result = await cleanup_service.cleanup_expired_videos(retention_days=30)
    
    # Assert
    assert result["soft_deleted"] == 0
    assert result["errors"] == 0
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_expired_videos_multiple(cleanup_service, mock_db_session):
    """Test cleanup with multiple expired videos."""
    # Arrange
    expired_videos = [
        VideoRecording(
            id=uuid4(),
            interview_id=uuid4(),
            storage_path=f"org_123/interview_{i}/recording.mp4",
            file_size_bytes=10_000_000,
            upload_completed_at=datetime.utcnow() - timedelta(days=35)
        )
        for i in range(3)
    ]
    
    cleanup_service._get_expired_videos = AsyncMock(return_value=expired_videos)
    
    # Act
    result = await cleanup_service.cleanup_expired_videos(retention_days=30)
    
    # Assert
    assert result["soft_deleted"] == 3
    assert result["errors"] == 0
    assert mock_db_session.add.call_count == 3
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_hard_delete_old_soft_deleted_videos_success(
    cleanup_service, 
    mock_db_session,
    mock_storage_client
):
    """Test successful hard deletion of old soft-deleted videos."""
    # Arrange
    soft_deleted_video = VideoRecording(
        id=uuid4(),
        interview_id=uuid4(),
        storage_path="org_123/interview_456/recording.mp4",
        deleted_at=datetime.utcnow() - timedelta(days=100)
    )
    
    cleanup_service._get_soft_deleted_before = AsyncMock(return_value=[soft_deleted_video])
    
    # Act
    result = await cleanup_service.hard_delete_old_soft_deleted_videos(days_after_soft_delete=90)
    
    # Assert
    assert result["hard_deleted"] == 1
    assert result["errors"] == 0
    mock_storage_client.delete_video.assert_called_once_with(soft_deleted_video.storage_path)
    mock_db_session.delete.assert_called_once_with(soft_deleted_video)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_hard_delete_storage_deletion_fails(
    cleanup_service,
    mock_db_session,
    mock_storage_client
):
    """Test hard delete continues even if storage deletion fails."""
    # Arrange
    soft_deleted_video = VideoRecording(
        id=uuid4(),
        interview_id=uuid4(),
        storage_path="org_123/interview_456/recording.mp4",
        deleted_at=datetime.utcnow() - timedelta(days=100)
    )
    
    cleanup_service._get_soft_deleted_before = AsyncMock(return_value=[soft_deleted_video])
    mock_storage_client.delete_video = AsyncMock(return_value=False)  # Storage deletion fails
    
    # Act
    result = await cleanup_service.hard_delete_old_soft_deleted_videos(days_after_soft_delete=90)
    
    # Assert - Should still proceed with database deletion
    assert result["hard_deleted"] == 1
    assert result["errors"] == 0
    mock_db_session.delete.assert_called_once_with(soft_deleted_video)


@pytest.mark.asyncio
async def test_hard_delete_no_videos(cleanup_service, mock_db_session):
    """Test hard delete when no old soft-deleted videos exist."""
    # Arrange
    cleanup_service._get_soft_deleted_before = AsyncMock(return_value=[])
    
    # Act
    result = await cleanup_service.hard_delete_old_soft_deleted_videos(days_after_soft_delete=90)
    
    # Assert
    assert result["hard_deleted"] == 0
    assert result["errors"] == 0
    mock_db_session.commit.assert_called_once()
