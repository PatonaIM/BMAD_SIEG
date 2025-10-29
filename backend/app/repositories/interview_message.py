"""Repository for InterviewMessage data access."""
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_message import InterviewMessage
from app.repositories.base import BaseRepository


class InterviewMessageRepository(BaseRepository[InterviewMessage]):
    """Repository for managing InterviewMessage records."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, InterviewMessage)

    async def get_by_session_id(self, session_id: UUID) -> List[InterviewMessage]:
        """
        Retrieve all messages for an interview session.

        Args:
            session_id: UUID of the interview session

        Returns:
            List of InterviewMessage records ordered by timestamp
        """
        result = await self.db.execute(
            select(InterviewMessage)
            .where(InterviewMessage.session_id == session_id)
            .order_by(InterviewMessage.timestamp)
        )
        return list(result.scalars().all())
