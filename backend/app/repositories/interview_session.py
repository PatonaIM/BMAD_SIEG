"""Repository for InterviewSession data access."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_session import InterviewSession
from app.repositories.base import BaseRepository


class InterviewSessionRepository(BaseRepository[InterviewSession]):
    """Repository for managing InterviewSession records."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, InterviewSession)

    async def get_by_interview_id(self, interview_id: UUID) -> Optional[InterviewSession]:
        """
        Retrieve interview session by interview ID.

        Args:
            interview_id: UUID of the interview

        Returns:
            InterviewSession if found, None otherwise
        """
        result = await self.db.execute(
            select(InterviewSession).where(InterviewSession.interview_id == interview_id)
        )
        return result.scalar_one_or_none()

    async def update_session_state(self, session: InterviewSession) -> InterviewSession:
        """
        Update session state in database.

        Args:
            session: InterviewSession with updated state

        Returns:
            Updated InterviewSession
        """
        await self.db.flush()
        await self.db.refresh(session)
        return session
