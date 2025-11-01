"""Service for cleaning up expired video recordings."""
from datetime import datetime, timedelta
from uuid import UUID

import structlog
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoRecording
from app.utils.supabase_storage import SupabaseStorageClient

logger = structlog.get_logger(__name__)


class VideoCleanupService:
    """Service for cleaning up expired videos."""

    def __init__(self, db_session: AsyncSession, storage_client: SupabaseStorageClient):
        """
        Initialize cleanup service.

        Args:
            db_session: Async database session
            storage_client: Supabase storage client instance
        """
        self.db = db_session
        self.storage = storage_client

    async def cleanup_expired_videos(self, retention_days: int = 30) -> dict:
        """
        Find and soft-delete videos older than retention period.

        Args:
            retention_days: Number of days to retain videos (default: 30)

        Returns:
            dict with counts of videos processed:
                - soft_deleted: Number of videos soft-deleted
                - errors: Number of errors encountered
        """
        soft_deleted = 0
        errors = 0
        
        try:
            # Get expired videos
            expired_videos = await self._get_expired_videos(retention_days)
            
            logger.info(
                "cleanup_expired_videos_started",
                retention_days=retention_days,
                candidates_count=len(expired_videos)
            )
            
            for video in expired_videos:
                try:
                    # Soft delete: set deleted_at timestamp
                    video.deleted_at = datetime.utcnow()
                    self.db.add(video)
                    
                    logger.info(
                        "video_soft_deleted",
                        interview_id=str(video.interview_id),
                        storage_path=video.storage_path,
                        file_size_mb=round(video.file_size_bytes / 1_000_000, 2) if video.file_size_bytes else None
                    )
                    soft_deleted += 1
                    
                except Exception as e:
                    logger.error(
                        "video_soft_delete_failed",
                        interview_id=str(video.interview_id),
                        error=str(e)
                    )
                    errors += 1
            
            # Commit all soft deletes
            await self.db.commit()
            
            logger.info(
                "cleanup_expired_videos_completed",
                soft_deleted=soft_deleted,
                errors=errors
            )
            
        except Exception as e:
            logger.error(
                "cleanup_expired_videos_failed",
                error=str(e)
            )
            errors += 1
        
        return {
            "soft_deleted": soft_deleted,
            "errors": errors
        }

    async def hard_delete_old_soft_deleted_videos(self, days_after_soft_delete: int = 90) -> dict:
        """
        Permanently delete videos soft-deleted more than specified days ago.

        Args:
            days_after_soft_delete: Days after soft delete before hard delete (default: 90)

        Returns:
            dict with counts of videos processed:
                - hard_deleted: Number of videos permanently deleted
                - errors: Number of errors encountered
        """
        hard_deleted = 0
        errors = 0
        
        try:
            # Get soft-deleted videos older than threshold
            old_soft_deleted = await self._get_soft_deleted_before(days_after_soft_delete)
            
            logger.info(
                "hard_delete_started",
                days_after_soft_delete=days_after_soft_delete,
                candidates_count=len(old_soft_deleted)
            )
            
            for video in old_soft_deleted:
                try:
                    # Delete from Supabase Storage
                    storage_deleted = await self.storage.delete_video(video.storage_path)
                    
                    if not storage_deleted:
                        logger.warning(
                            "storage_deletion_failed_but_continuing",
                            video_id=str(video.id),
                            storage_path=video.storage_path
                        )
                    
                    # Delete database record permanently
                    await self.db.delete(video)
                    
                    logger.info(
                        "video_hard_deleted",
                        video_id=str(video.id),
                        interview_id=str(video.interview_id),
                        storage_path=video.storage_path
                    )
                    hard_deleted += 1
                    
                except Exception as e:
                    logger.error(
                        "video_hard_delete_failed",
                        video_id=str(video.id),
                        error=str(e)
                    )
                    errors += 1
            
            # Commit all hard deletes
            await self.db.commit()
            
            logger.info(
                "hard_delete_completed",
                hard_deleted=hard_deleted,
                errors=errors
            )
            
        except Exception as e:
            logger.error(
                "hard_delete_failed",
                error=str(e)
            )
            errors += 1
        
        return {
            "hard_deleted": hard_deleted,
            "errors": errors
        }

    async def _get_expired_videos(self, retention_days: int) -> list[VideoRecording]:
        """
        Query videos older than retention period.

        Args:
            retention_days: Number of days to retain videos

        Returns:
            List of VideoRecording instances
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        stmt = select(VideoRecording).where(
            and_(
                VideoRecording.upload_completed_at < cutoff_date,
                VideoRecording.upload_completed_at.isnot(None),
                VideoRecording.deleted_at.is_(None)
            )
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_soft_deleted_before(self, days_ago: int) -> list[VideoRecording]:
        """
        Get soft-deleted videos older than specified days.

        Args:
            days_ago: Number of days after soft delete

        Returns:
            List of VideoRecording instances
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
        
        stmt = select(VideoRecording).where(
            and_(
                VideoRecording.deleted_at < cutoff_date,
                VideoRecording.deleted_at.isnot(None)
            )
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
