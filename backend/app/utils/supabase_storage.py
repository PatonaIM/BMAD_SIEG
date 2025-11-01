"""Supabase Storage client utility for video operations."""
import structlog
from supabase import Client, create_client

from app.core.config import settings

logger = structlog.get_logger(__name__)


class SupabaseStorageClient:
    """Utility for Supabase Storage operations."""

    def __init__(self):
        """Initialize Supabase client with service role key."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        self.bucket_name = "interview-recordings"

    async def upload_video(
        self,
        video_data: bytes,
        org_id: str,
        interview_id: str
    ) -> str:
        """
        Upload complete video file to storage.

        Args:
            video_data: Video file bytes
            org_id: Organization ID
            interview_id: Interview ID

        Returns:
            Storage path of uploaded video

        Raises:
            Exception: If upload fails
        """
        # Construct storage path: {org_id}/{interview_id}/recording.mp4
        file_path = f"{org_id}/{interview_id}/recording.mp4"

        try:
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=video_data,
                file_options={"content-type": "video/mp4"}
            )

            logger.info(
                "video_uploaded",
                file_path=file_path,
                size_bytes=len(video_data),
                org_id=org_id,
                interview_id=interview_id
            )
            return file_path
        except Exception as e:
            logger.error(
                "video_upload_failed",
                file_path=file_path,
                org_id=org_id,
                interview_id=interview_id,
                error=str(e)
            )
            raise

    async def upload_video_chunk(
        self, 
        file_path: str, 
        file_data: bytes
    ) -> str:
        """
        Upload video chunk to storage.

        Args:
            file_path: Storage path (e.g., "org_id/interview_id/recording.mp4")
            file_data: Video file bytes

        Returns:
            Storage path of uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            response = self.client.storage.from_(self.bucket_name).upload(
                path=file_path,
                file=file_data,
                file_options={"content-type": "video/mp4"}
            )
            
            logger.info(
                "video_uploaded",
                file_path=file_path,
                size_bytes=len(file_data)
            )
            return file_path
        except Exception as e:
            logger.error(
                "video_upload_failed",
                file_path=file_path,
                error=str(e)
            )
            raise

    async def generate_signed_url(
        self, 
        file_path: str, 
        expires_in: int = 86400  # 24 hours
    ) -> str:
        """
        Generate temporary signed URL for video access.

        Args:
            file_path: Storage path of the video file
            expires_in: URL expiration time in seconds (default: 24 hours)

        Returns:
            Signed URL string

        Raises:
            Exception: If URL generation fails
        """
        try:
            response = self.client.storage.from_(self.bucket_name).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            signed_url = response.get("signedURL")
            
            logger.info(
                "signed_url_generated",
                file_path=file_path,
                expires_in=expires_in
            )
            return signed_url
        except Exception as e:
            logger.error(
                "signed_url_generation_failed",
                file_path=file_path,
                error=str(e)
            )
            raise

    async def delete_video(self, file_path: str) -> bool:
        """
        Delete video from storage.

        Args:
            file_path: Storage path of the video to delete

        Returns:
            True if deletion successful, False otherwise

        Raises:
            Exception: If deletion fails critically
        """
        try:
            response = self.client.storage.from_(self.bucket_name).remove([file_path])
            
            logger.info(
                "video_deleted_from_storage",
                file_path=file_path
            )
            return True
        except Exception as e:
            logger.error(
                "video_deletion_failed",
                file_path=file_path,
                error=str(e)
            )
            return False

    async def get_bucket_usage(self) -> dict:
        """
        Get storage usage statistics.

        Returns:
            dict with:
                - total_size_bytes: Total storage used in bytes
                - total_size_gb: Total storage used in GB
                - file_count: Number of files in bucket

        Note: This is an approximation based on listing files.
        For accurate usage, use Supabase dashboard.
        """
        try:
            files = self.client.storage.from_(self.bucket_name).list()
            
            total_size = 0
            file_count = 0
            
            # Recursively count files and sizes
            def count_files(items):
                nonlocal total_size, file_count
                for item in items:
                    if item.get("id"):  # It's a file
                        file_count += 1
                        # Size might not be available in list response
                        # This is a limitation of Supabase storage API
            
            count_files(files)
            
            usage = {
                "total_size_bytes": total_size,
                "total_size_gb": round(total_size / (1024 ** 3), 3),
                "file_count": file_count
            }
            
            logger.info(
                "bucket_usage_retrieved",
                usage=usage
            )
            return usage
        except Exception as e:
            logger.error(
                "bucket_usage_retrieval_failed",
                error=str(e)
            )
            return {
                "total_size_bytes": 0,
                "total_size_gb": 0.0,
                "file_count": 0
            }
