"""Repository for ResumeAnalysis data access."""
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume_analysis import ResumeAnalysis
from app.repositories.base import BaseRepository


class ResumeAnalysisRepository(BaseRepository[ResumeAnalysis]):
    """Repository for ResumeAnalysis data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, ResumeAnalysis)

    async def get_latest_by_resume_id(self, resume_id: UUID) -> ResumeAnalysis | None:
        """
        Get the most recent analysis for a resume.

        Args:
            resume_id: UUID of the resume

        Returns:
            Latest ResumeAnalysis instance or None if not found
        """
        result = await self.db.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .order_by(desc(ResumeAnalysis.analyzed_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_by_resume_id(self, resume_id: UUID) -> list[ResumeAnalysis]:
        """
        Get all analyses for a resume (historical).

        Args:
            resume_id: UUID of the resume

        Returns:
            List of ResumeAnalysis instances ordered by analyzed_at DESC
        """
        result = await self.db.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == resume_id)
            .order_by(desc(ResumeAnalysis.analyzed_at))
        )
        return list(result.scalars().all())
