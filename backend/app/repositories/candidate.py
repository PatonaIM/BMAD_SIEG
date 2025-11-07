"""Repository for Candidate data access."""

from uuid import UUID

from sqlalchemy import select, update
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

    async def update_embedding(
        self, 
        candidate_id: UUID, 
        embedding: list[float]
    ) -> None:
        """
        Update candidate profile embedding vector.
        
        Args:
            candidate_id: UUID of the candidate
            embedding: 3072-dimensional embedding vector
        """
        stmt = (
            update(Candidate)
            .where(Candidate.id == candidate_id)
            .values(profile_embedding=embedding)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_candidates_for_embedding(
        self,
        skip_with_embedding: bool,
        limit: int
    ) -> list[Candidate]:
        """
        Get candidates ready for embedding generation.
        
        Filters:
        - profile_completeness_score >= 40% (sufficient data)
        - Optionally skip candidates with existing embeddings
        
        Args:
            skip_with_embedding: If true, skip candidates with existing embeddings
            limit: Max number of candidates to return
        
        Returns:
            List of Candidate instances
        """
        stmt = select(Candidate).where(
            Candidate.profile_completeness_score >= 40
        )
        
        if skip_with_embedding:
            stmt = stmt.where(Candidate.profile_embedding.is_(None))
        
        stmt = stmt.limit(limit).order_by(Candidate.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
