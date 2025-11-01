"""Repository for InterviewSession data access."""
from datetime import datetime
from typing import Any
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

    async def get_by_interview_id(self, interview_id: UUID) -> InterviewSession | None:
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

    async def update_session_state(
        self,
        session: InterviewSession,
        conversation_memory: dict[str, Any] | None = None,
        skill_boundaries: dict[str, Any] | None = None,
        progression_state: dict[str, Any] | None = None
    ) -> InterviewSession:
        """
        Update session state fields.

        Args:
            session: InterviewSession to update
            conversation_memory: Updated conversation memory JSONB
            skill_boundaries: Updated skill boundaries JSONB
            progression_state: Updated progression state JSONB

        Returns:
            Updated InterviewSession
        """
        if conversation_memory is not None:
            session.conversation_memory = conversation_memory

        if skill_boundaries is not None:
            session.skill_boundaries_identified = skill_boundaries

        if progression_state is not None:
            session.progression_state = progression_state

        session.last_activity_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def update_last_activity(
        self,
        session_id: UUID,
        timestamp: datetime | None = None
    ) -> None:
        """
        Update last activity timestamp.

        Args:
            session_id: UUID of the session
            timestamp: Timestamp to set (defaults to now)
        """
        session = await self.get_by_id(session_id)
        if session:
            session.last_activity_at = timestamp or datetime.utcnow()
            await self.db.flush()

    async def increment_question_count(self, session_id: UUID) -> int:
        """
        Increment questions asked count.

        Args:
            session_id: UUID of the session

        Returns:
            Updated question count
        """
        session = await self.get_by_id(session_id)
        if session:
            session.questions_asked_count += 1
            await self.db.flush()
            return session.questions_asked_count
        return 0
