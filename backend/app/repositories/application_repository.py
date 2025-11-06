"""Repository for Application data access."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    """Repository for Application data access."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        super().__init__(db, Application)

    async def get_by_id(self, application_id: UUID) -> Application | None:
        """
        Retrieve application by ID with eager-loaded job_posting relationship.

        Args:
            application_id: UUID of the application

        Returns:
            Application instance with eager-loaded job_posting if found, None otherwise
        """
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(selectinload(Application.job_posting))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_candidate_id(
        self, candidate_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Application]:
        """
        Get applications by candidate ID with pagination.

        Args:
            candidate_id: UUID of the candidate
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of Application instances with eager-loaded relationships
        """
        stmt = (
            select(Application)
            .options(
                selectinload(Application.job_posting),
                selectinload(Application.interview)
            )
            .where(Application.candidate_id == candidate_id)
            .offset(skip)
            .limit(limit)
            .order_by(Application.applied_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_job_posting_id(
        self, job_posting_id: UUID, skip: int = 0, limit: int = 20
    ) -> list[Application]:
        """
        Get applications by job posting ID with pagination.

        Args:
            job_posting_id: UUID of the job posting
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20)

        Returns:
            List of Application instances with eager-loaded relationships
        """
        stmt = (
            select(Application)
            .options(
                selectinload(Application.candidate),
                selectinload(Application.interview)
            )
            .where(Application.job_posting_id == job_posting_id)
            .offset(skip)
            .limit(limit)
            .order_by(Application.applied_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def check_existing_application(
        self, candidate_id: UUID, job_posting_id: UUID
    ) -> Application | None:
        """
        Check if application already exists for candidate and job posting.

        Args:
            candidate_id: UUID of the candidate
            job_posting_id: UUID of the job posting

        Returns:
            Existing Application if found, None otherwise
        """
        stmt = select(Application).where(
            Application.candidate_id == candidate_id,
            Application.job_posting_id == job_posting_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, application_id: UUID, status: str) -> Application:
        """
        Update application status.

        Args:
            application_id: UUID of the application
            status: New status value

        Returns:
            Updated Application instance

        Raises:
            ValueError: If application not found
        """
        application = await self.get_by_id(application_id)
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application.status = status
        await self.db.flush()
        await self.db.refresh(application)
        return application

    async def link_interview(
        self, application_id: UUID, interview_id: UUID
    ) -> Application:
        """
        Link interview to application and update status to interview_scheduled.

        Args:
            application_id: UUID of the application
            interview_id: UUID of the interview to link

        Returns:
            Updated Application instance

        Raises:
            ValueError: If application not found
        """
        application = await self.get_by_id(application_id)
        if not application:
            raise ValueError(f"Application {application_id} not found")

        application.interview_id = interview_id
        application.status = "interview_scheduled"
        await self.db.flush()
        await self.db.refresh(application)
        return application
