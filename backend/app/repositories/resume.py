"""Repository for Resume data access."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, Resume)

    async def update_parsing_status(
        self,
        resume_id: UUID,
        status: str,
        parsed_at: datetime | None,
        parsed_data: dict | None,
    ) -> Resume:
        """
        Update resume parsing results.

        Args:
            resume_id: UUID of the resume
            status: Parsing status (pending, processing, completed, failed)
            parsed_at: Timestamp when parsing completed
            parsed_data: Structured parsed data as dict

        Returns:
            Updated Resume instance

        Raises:
            ValueError: If resume not found
        """
        resume = await self.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        resume.parsing_status = status
        resume.parsed_at = parsed_at
        resume.parsed_data = parsed_data

        await self.db.commit()
        await self.db.refresh(resume)
        return resume

    async def get_by_candidate_id(self, candidate_id: UUID) -> list[Resume]:
        """
        Get all resumes for a candidate.

        Args:
            candidate_id: UUID of the candidate

        Returns:
            List of Resume instances
        """
        result = await self.db.execute(
            select(Resume).where(Resume.candidate_id == candidate_id)
        )
        return list(result.scalars().all())
