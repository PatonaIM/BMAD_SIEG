"""Business logic for job posting operations."""

from uuid import UUID

import structlog
from fastapi import HTTPException, status

from app.models.job_posting import JobPosting
from app.repositories.job_posting_repository import JobPostingRepository


class JobPostingService:
    """Service for job posting business logic."""

    def __init__(self, repo: JobPostingRepository):
        """
        Initialize job posting service with repository.

        Args:
            repo: JobPostingRepository instance
        """
        self.repo = repo
        self.logger = structlog.get_logger().bind(service="job_posting_service")

    async def get_job_posting_by_id(self, job_id: UUID) -> JobPosting:
        """
        Get job posting by ID or raise 404.

        Args:
            job_id: UUID of the job posting

        Returns:
            JobPosting instance

        Raises:
            HTTPException: 404 if job posting not found
        """
        self.logger.info("fetching_job_posting", job_id=str(job_id))

        job = await self.repo.get_by_id(job_id)
        if not job:
            self.logger.warning("job_posting_not_found", job_id=str(job_id))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting {job_id} not found"
            )

        return job

    async def get_active_job_postings(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[list[JobPosting], int]:
        """
        Get active job postings with pagination.

        Args:
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20, max: 100)

        Returns:
            Tuple of (list of JobPosting instances, total count)

        Raises:
            HTTPException: 400 if skip is negative or limit exceeds maximum
        """
        # Validate input
        if skip < 0:
            self.logger.warning("invalid_skip", skip=skip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip must be non-negative"
            )

        # Cap limit at 100
        if limit > 100:
            self.logger.info("limit_capped", requested=limit, capped=100)
            limit = 100
        elif limit < 1:
            self.logger.warning("invalid_limit", limit=limit)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be at least 1"
            )

        self.logger.info("fetching_active_jobs", skip=skip, limit=limit)

        # Get data
        jobs = await self.repo.get_active(skip=skip, limit=limit)
        total = await self.repo.count_active()

        self.logger.info(
            "active_jobs_fetched",
            returned=len(jobs),
            total=total,
            skip=skip,
            limit=limit
        )

        return jobs, total

    async def search_and_filter_jobs(
        self, filters: dict, skip: int = 0, limit: int = 20
    ) -> tuple[list[JobPosting], int]:
        """
        Search and filter job postings with multiple criteria.

        Supports filtering by:
        - role_category: Exact match on role_category enum
        - tech_stack: Case-insensitive partial match
        - employment_type: Exact match on employment_type enum
        - work_setup: Exact match on work_setup enum
        - experience_level: Exact match on experience_level string
        - location: Case-insensitive partial match
        - search: Search in title OR company (case-insensitive)

        Args:
            filters: Dictionary of filter criteria
            skip: Number of records to skip for pagination (default: 0)
            limit: Maximum number of records to return (default: 20, max: 100)

        Returns:
            Tuple of (list of matching JobPosting instances, total count)

        Raises:
            HTTPException: 400 if validation fails
        """
        # Validate input
        if skip < 0:
            self.logger.warning("invalid_skip", skip=skip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip must be non-negative"
            )

        # Cap limit at 100
        if limit > 100:
            self.logger.info("limit_capped", requested=limit, capped=100)
            limit = 100
        elif limit < 1:
            self.logger.warning("invalid_limit", limit=limit)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be at least 1"
            )

        # Validate enum filters
        valid_role_categories = [
            'engineering', 'quality_assurance', 'data', 'devops', 'design',
            'product', 'sales', 'support', 'operations', 'management', 'other'
        ]
        valid_employment_types = ['permanent', 'contract', 'part_time']
        valid_work_setups = ['remote', 'hybrid', 'onsite']

        if filters.get('role_category') and filters['role_category'] not in valid_role_categories:
            self.logger.warning("invalid_role_category", value=filters['role_category'])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role_category. Must be one of: {', '.join(valid_role_categories)}"
            )

        if filters.get('employment_type') and filters['employment_type'] not in valid_employment_types:
            self.logger.warning("invalid_employment_type", value=filters['employment_type'])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid employment_type. Must be one of: {', '.join(valid_employment_types)}"
            )

        if filters.get('work_setup') and filters['work_setup'] not in valid_work_setups:
            self.logger.warning("invalid_work_setup", value=filters['work_setup'])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid work_setup. Must be one of: {', '.join(valid_work_setups)}"
            )

        self.logger.info("searching_jobs", filters=filters, skip=skip, limit=limit)

        # Execute search
        jobs, total = await self.repo.filter_advanced(filters, skip, limit)

        self.logger.info(
            "jobs_searched",
            returned=len(jobs),
            total=total,
            skip=skip,
            limit=limit
        )

        return jobs, total
