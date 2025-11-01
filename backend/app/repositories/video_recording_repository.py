"""Repository for VideoRecording data access."""
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VideoRecording
from app.repositories.base import BaseRepository


class VideoRecordingRepository(BaseRepository[VideoRecording]):
    """Repository for video recording data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, VideoRecording)

    async def get_by_interview_id(self, interview_id: UUID) -> VideoRecording | None:
        """
        Get video recording for an interview (exclude soft-deleted).

        Args:
            interview_id: UUID of the interview

        Returns:
            VideoRecording instance if found, None otherwise
        """
        stmt = select(VideoRecording).where(
            and_(
                VideoRecording.interview_id == interview_id,
                VideoRecording.deleted_at.is_(None)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_expired_videos(self, retention_days: int) -> list[VideoRecording]:
        """
        Get videos older than retention period (not soft-deleted).

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

    async def get_soft_deleted_before(self, days_ago: int) -> list[VideoRecording]:
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

    async def soft_delete(self, video_id: UUID) -> VideoRecording | None:
        """
        Mark video as deleted (set deleted_at).

        Args:
            video_id: UUID of the video to soft delete

        Returns:
            Updated VideoRecording instance if found, None otherwise
        """
        video = await self.get_by_id(video_id)
        if video:
            video.deleted_at = datetime.utcnow()
            self.db.add(video)
            await self.db.flush()
            await self.db.refresh(video)
            return video
        return None

    async def hard_delete(self, video_id: UUID) -> bool:
        """
        Permanently delete video record from database.

        Args:
            video_id: UUID of the video to hard delete

        Returns:
            True if deleted, False if not found
        """
        return await self.delete(video_id)
