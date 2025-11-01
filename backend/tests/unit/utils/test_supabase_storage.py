"""Unit tests for SupabaseStorageClient."""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.utils.supabase_storage import SupabaseStorageClient


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client."""
    with patch("app.utils.supabase_storage.create_client") as mock_create:
        mock_client = Mock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def storage_client(mock_supabase_client):
    """Create SupabaseStorageClient with mocked Supabase client."""
    return SupabaseStorageClient()


@pytest.mark.asyncio
async def test_upload_video_chunk_success(storage_client, mock_supabase_client):
    """Test successful video upload."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    file_data = b"video_data_here"
    
    mock_bucket = Mock()
    mock_bucket.upload = Mock(return_value={"path": file_path})
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.upload_video_chunk(file_path, file_data)
    
    # Assert
    assert result == file_path
    mock_bucket.upload.assert_called_once()


@pytest.mark.asyncio
async def test_upload_video_chunk_failure(storage_client, mock_supabase_client):
    """Test video upload failure."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    file_data = b"video_data_here"
    
    mock_bucket = Mock()
    mock_bucket.upload = Mock(side_effect=Exception("Upload failed"))
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act & Assert
    with pytest.raises(Exception, match="Upload failed"):
        await storage_client.upload_video_chunk(file_path, file_data)


@pytest.mark.asyncio
async def test_generate_signed_url_success(storage_client, mock_supabase_client):
    """Test signed URL generation."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    expected_url = "https://supabase.co/storage/signed/abc123"
    
    mock_bucket = Mock()
    mock_bucket.create_signed_url = Mock(return_value={"signedURL": expected_url})
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.generate_signed_url(file_path, expires_in=3600)
    
    # Assert
    assert result == expected_url
    mock_bucket.create_signed_url.assert_called_once_with(
        path=file_path,
        expires_in=3600
    )


@pytest.mark.asyncio
async def test_generate_signed_url_default_expiry(storage_client, mock_supabase_client):
    """Test signed URL generation with default expiry."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    expected_url = "https://supabase.co/storage/signed/abc123"
    
    mock_bucket = Mock()
    mock_bucket.create_signed_url = Mock(return_value={"signedURL": expected_url})
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.generate_signed_url(file_path)
    
    # Assert
    assert result == expected_url
    mock_bucket.create_signed_url.assert_called_once_with(
        path=file_path,
        expires_in=86400  # 24 hours default
    )


@pytest.mark.asyncio
async def test_delete_video_success(storage_client, mock_supabase_client):
    """Test successful video deletion."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    
    mock_bucket = Mock()
    mock_bucket.remove = Mock(return_value=[{"name": file_path}])
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.delete_video(file_path)
    
    # Assert
    assert result is True
    mock_bucket.remove.assert_called_once_with([file_path])


@pytest.mark.asyncio
async def test_delete_video_failure(storage_client, mock_supabase_client):
    """Test video deletion failure."""
    # Arrange
    file_path = "org_123/interview_456/recording.mp4"
    
    mock_bucket = Mock()
    mock_bucket.remove = Mock(side_effect=Exception("Delete failed"))
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.delete_video(file_path)
    
    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_get_bucket_usage_success(storage_client, mock_supabase_client):
    """Test bucket usage retrieval."""
    # Arrange
    mock_files = [
        {"id": "file1", "name": "video1.mp4"},
        {"id": "file2", "name": "video2.mp4"},
    ]
    
    mock_bucket = Mock()
    mock_bucket.list = Mock(return_value=mock_files)
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.get_bucket_usage()
    
    # Assert
    assert result["file_count"] == 2
    assert "total_size_gb" in result
    assert "total_size_bytes" in result


@pytest.mark.asyncio
async def test_get_bucket_usage_failure(storage_client, mock_supabase_client):
    """Test bucket usage retrieval failure."""
    # Arrange
    mock_bucket = Mock()
    mock_bucket.list = Mock(side_effect=Exception("List failed"))
    mock_supabase_client.storage.from_ = Mock(return_value=mock_bucket)
    
    # Act
    result = await storage_client.get_bucket_usage()
    
    # Assert - Should return zero values on error
    assert result["file_count"] == 0
    assert result["total_size_gb"] == 0.0
    assert result["total_size_bytes"] == 0
