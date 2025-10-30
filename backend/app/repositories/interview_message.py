"""Repository for InterviewMessage data access."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
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
            List of InterviewMessage records ordered by sequence number
        """
        result = await self.db.execute(
            select(InterviewMessage)
            .where(InterviewMessage.session_id == session_id)
            .order_by(InterviewMessage.sequence_number)
        )
        return list(result.scalars().all())

    async def get_by_interview_id(self, interview_id: UUID) -> List[InterviewMessage]:
        """
        Retrieve all messages for an interview.

        Args:
            interview_id: UUID of the interview

        Returns:
            List of InterviewMessage records ordered by sequence number
        """
        result = await self.db.execute(
            select(InterviewMessage)
            .where(InterviewMessage.interview_id == interview_id)
            .order_by(InterviewMessage.sequence_number)
        )
        return list(result.scalars().all())

    async def get_latest_message(self, interview_id: UUID) -> Optional[InterviewMessage]:
        """
        Get the most recent message for an interview.

        Args:
            interview_id: UUID of the interview

        Returns:
            Latest InterviewMessage or None if no messages exist
        """
        result = await self.db.execute(
            select(InterviewMessage)
            .where(InterviewMessage.interview_id == interview_id)
            .order_by(InterviewMessage.sequence_number.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_message(
        self,
        interview_id: UUID,
        session_id: UUID,
        message_type: str,
        content_text: str,
        sequence_number: int,
        content_audio_url: Optional[str] = None,
        audio_duration_seconds: Optional[int] = None
    ) -> InterviewMessage:
        """
        Create a new interview message.

        Args:
            interview_id: UUID of the interview
            session_id: UUID of the interview session
            message_type: Type of message ('ai_question' or 'candidate_response')
            content_text: Text content of the message
            sequence_number: Order in the conversation
            content_audio_url: Optional URL to audio file
            audio_duration_seconds: Optional duration of audio

        Returns:
            Created InterviewMessage
        """
        message = InterviewMessage(
            interview_id=interview_id,
            session_id=session_id,
            message_type=message_type,
            content_text=content_text,
            sequence_number=sequence_number,
            content_audio_url=content_audio_url,
            audio_duration_seconds=audio_duration_seconds,
            created_at=datetime.utcnow()
        )
        
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        
        return message

    async def get_message_count_for_session(self, session_id: UUID) -> int:
        """
        Get the total count of messages for a session.

        Args:
            session_id: UUID of the interview session

        Returns:
            Count of messages in the session
        """
        result = await self.db.execute(
            select(func.count(InterviewMessage.id))
            .where(InterviewMessage.session_id == session_id)
        )
        return result.scalar() or 0
