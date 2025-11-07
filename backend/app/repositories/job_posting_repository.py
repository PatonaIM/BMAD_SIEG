"""Repository for JobPosting data access."""

from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting
from app.repositories.base import BaseRepository


class JobPostingRepository(BaseRepository[JobPosting]):
    """Repository for JobPosting data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, JobPosting)

    async def get_all(self, skip: int = 0, limit: int = 20) -> list[JobPosting]:
        """
        Get all job postings with pagination.

        Args:
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of JobPosting instances
        """
        stmt = (
            select(JobPosting)
            .offset(skip)
            .limit(limit)
            .order_by(JobPosting.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active(self, skip: int = 0, limit: int = 20) -> list[JobPosting]:
        """
        Get active job postings with pagination.

        Only returns job postings with status = 'active'.

        Args:
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of active JobPosting instances
        """
        stmt = (
            select(JobPosting)
            .where(JobPosting.status == 'active')
            .offset(skip)
            .limit(limit)
            .order_by(JobPosting.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def filter_by_role_category(
        self, role_category: str, skip: int = 0, limit: int = 20
    ) -> list[JobPosting]:
        """
        Filter job postings by role category.

        Only returns active job postings matching the specified role category.

        Args:
            role_category: Role category to filter by (e.g., 'engineering', 'data')
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of matching JobPosting instances
        """
        stmt = (
            select(JobPosting)
            .where(JobPosting.role_category == role_category)
            .where(JobPosting.status == 'active')
            .offset(skip)
            .limit(limit)
            .order_by(JobPosting.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def filter_by_location(
        self, location: str, skip: int = 0, limit: int = 20
    ) -> list[JobPosting]:
        """
        Filter job postings by location with partial match.

        Performs case-insensitive partial matching on location field.
        Only returns active job postings.

        Args:
            location: Location string to search for (partial match)
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of matching JobPosting instances
        """
        stmt = (
            select(JobPosting)
            .where(JobPosting.location.ilike(f'%{location}%'))
            .where(JobPosting.status == 'active')
            .offset(skip)
            .limit(limit)
            .order_by(JobPosting.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def search(
        self, query: str, skip: int = 0, limit: int = 20
    ) -> list[JobPosting]:
        """
        Search job postings by title or company name.

        Performs case-insensitive partial match on title and company fields.
        Only returns active job postings.

        Args:
            query: Search term to match against title or company
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of matching JobPosting instances
        """
        search_pattern = f'%{query}%'
        stmt = (
            select(JobPosting)
            .where(
                or_(
                    JobPosting.title.ilike(search_pattern),
                    JobPosting.company.ilike(search_pattern)
                )
            )
            .where(JobPosting.status == 'active')
            .offset(skip)
            .limit(limit)
            .order_by(JobPosting.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """
        Count the total number of active job postings.

        Returns:
            Number of active job postings
        """
        stmt = select(func.count()).where(JobPosting.status == 'active')
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def filter_advanced(
        self, filters: dict, skip: int, limit: int
    ) -> tuple[list[JobPosting], int]:
        """
        Filter job postings with multiple criteria and return results with total count.

        Supports filtering by:
        - role_category: Exact match on role_category enum
        - tech_stack: Case-insensitive partial match
        - employment_type: Exact match on employment_type enum
        - work_setup: Exact match on work_setup enum
        - experience_level: Exact match on experience_level string
        - location: Case-insensitive partial match
        - search: Search in title OR company (case-insensitive)

        All filters are applied with AND logic.
        Always filters for status = 'active'.
        Results ordered by created_at DESC (newest first).

        Args:
            filters: Dictionary of filter criteria
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of matching JobPosting instances, total count)
        """
        # Build base query for active jobs
        stmt = select(JobPosting).where(JobPosting.status == 'active')
        count_stmt = select(func.count()).where(JobPosting.status == 'active')

        # Apply filters conditionally
        if filters.get('role_category'):
            stmt = stmt.where(JobPosting.role_category == filters['role_category'])
            count_stmt = count_stmt.where(JobPosting.role_category == filters['role_category'])

        if filters.get('tech_stack'):
            tech_pattern = f"%{filters['tech_stack']}%"
            stmt = stmt.where(JobPosting.tech_stack.ilike(tech_pattern))
            count_stmt = count_stmt.where(JobPosting.tech_stack.ilike(tech_pattern))

        if filters.get('employment_type'):
            stmt = stmt.where(JobPosting.employment_type == filters['employment_type'])
            count_stmt = count_stmt.where(JobPosting.employment_type == filters['employment_type'])

        if filters.get('work_setup'):
            stmt = stmt.where(JobPosting.work_setup == filters['work_setup'])
            count_stmt = count_stmt.where(JobPosting.work_setup == filters['work_setup'])

        if filters.get('experience_level'):
            stmt = stmt.where(JobPosting.experience_level == filters['experience_level'])
            count_stmt = count_stmt.where(JobPosting.experience_level == filters['experience_level'])

        if filters.get('location'):
            loc_pattern = f"%{filters['location']}%"
            stmt = stmt.where(JobPosting.location.ilike(loc_pattern))
            count_stmt = count_stmt.where(JobPosting.location.ilike(loc_pattern))

        if filters.get('search'):
            search_pattern = f"%{filters['search']}%"
            search_condition = or_(
                JobPosting.title.ilike(search_pattern),
                JobPosting.company.ilike(search_pattern)
            )
            stmt = stmt.where(search_condition)
            count_stmt = count_stmt.where(search_condition)

        # Apply ordering and pagination
        stmt = stmt.order_by(JobPosting.created_at.desc()).offset(skip).limit(limit)

        # Execute queries
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        data_result = await self.db.execute(stmt)
        items = list(data_result.scalars().all())

        return items, total

    async def update_embedding(
        self, 
        job_id: UUID, 
        embedding: list[float]
    ) -> None:
        """
        Update job posting embedding vector.
        
        Args:
            job_id: UUID of the job posting
            embedding: 3072-dimensional embedding vector
        """
        stmt = (
            update(JobPosting)
            .where(JobPosting.id == job_id)
            .values(job_embedding=embedding)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_jobs_for_embedding(
        self,
        skip_with_embedding: bool,
        limit: int
    ) -> list[JobPosting]:
        """
        Get active job postings ready for embedding generation.
        
        Filters:
        - status = 'active'
        - Optionally skip jobs with existing embeddings
        
        Args:
            skip_with_embedding: If true, skip jobs with existing embeddings
            limit: Max number of jobs to return
        
        Returns:
            List of JobPosting instances
        """
        stmt = select(JobPosting).where(
            JobPosting.status == 'active'
        )
        
        if skip_with_embedding:
            stmt = stmt.where(JobPosting.job_embedding.is_(None))
        
        stmt = stmt.limit(limit).order_by(JobPosting.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

        return items, total
