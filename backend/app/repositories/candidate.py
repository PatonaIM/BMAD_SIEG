"""Repository for Candidate data access."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.repositories.base import BaseRepository


class CandidateRepository(BaseRepository[Candidate]):
    """Repository for Candidate data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, Candidate)

    async def get_by_email(self, email: str) -> Candidate | None:
        """
        Find candidate by email address.

        Args:
            email: Email address to search for

        Returns:
            Candidate instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Candidate).where(Candidate.email == email)
        )
        return result.scalar_one_or_none()
