"""Repository for Interview data access."""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.interview import Interview
from app.repositories.base import BaseRepository


class InterviewRepository(BaseRepository[Interview]):
    """Repository for managing Interview records."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, Interview)

    async def get_by_id_with_session(self, interview_id: UUID) -> Interview | None:
        """
        Retrieve interview with eagerly loaded session.

        Args:
            interview_id: UUID of the interview

        Returns:
            Interview with session relationship loaded, None if not found
        """
        result = await self.db.execute(
            select(Interview)
            .where(Interview.id == interview_id)
            .options(joinedload(Interview.session))
        )
        return result.scalar_one_or_none()

    async def update_token_usage(
        self,
        interview_id: UUID,
        tokens_used: int,
        cost_usd: Decimal
    ) -> None:
        """
        Update interview token usage and cost.

        Args:
            interview_id: UUID of the interview
            tokens_used: Number of tokens to add
            cost_usd: Cost in USD to add
        """
        interview = await self.get_by_id(interview_id)
        if interview:
            interview.total_tokens_used += tokens_used
            interview.cost_usd = (interview.cost_usd or Decimal(0)) + cost_usd
            await self.db.flush()

    async def get_by_candidate_id(self, candidate_id: UUID) -> list[Interview]:
        """
        Retrieve all interviews for a candidate.

        Args:
            candidate_id: UUID of the candidate

        Returns:
            List of Interview records
        """
        result = await self.db.execute(
            select(Interview)
            .where(Interview.candidate_id == candidate_id)
            .order_by(Interview.created_at.desc())
        )
        return list(result.scalars().all())
