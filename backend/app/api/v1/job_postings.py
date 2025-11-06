"""Job posting API routes."""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from app.api.deps import get_job_posting_service
from app.schemas.job_posting import (
    JobPostingFilters,
    JobPostingListResponse,
    JobPostingResponse,
)
from app.services.job_posting_service import JobPostingService

logger = structlog.get_logger().bind(module="job_postings_api")

router = APIRouter(prefix="/job-postings", tags=["job-postings"])


@router.get("/", response_model=JobPostingListResponse)
async def list_job_postings(
    filters: Annotated[JobPostingFilters, Depends()],
    service: Annotated[JobPostingService, Depends(get_job_posting_service)]
) -> JobPostingListResponse:
    """
    List job postings with optional filtering and pagination.

    This endpoint returns active job postings matching the specified filters.
    All filters are optional and can be combined using AND logic.

    **Filtering Options:**
    - **role_category**: Filter by job category (engineering, data, etc.)
    - **tech_stack**: Filter by technology (case-insensitive partial match)
    - **employment_type**: Filter by employment type (permanent, contract, part_time)
    - **work_setup**: Filter by work arrangement (remote, hybrid, onsite)
    - **experience_level**: Filter by required experience level
    - **location**: Filter by location (case-insensitive partial match)
    - **search**: Search in job title and company name

    **Pagination:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Max records to return (default: 20, max: 100)

    Returns paginated list with total count for frontend pagination.

    Args:
        filters: Query parameters for filtering and pagination
        service: JobPostingService instance (injected)

    Returns:
        JobPostingListResponse with jobs, total count, skip, and limit
    """
    logger.info(
        "listing_job_postings",
        role_category=filters.role_category,
        tech_stack=filters.tech_stack,
        employment_type=filters.employment_type,
        work_setup=filters.work_setup,
        experience_level=filters.experience_level,
        location=filters.location,
        search=filters.search,
        skip=filters.skip,
        limit=filters.limit
    )

    # Build filter dict excluding None values
    filter_dict = {
        k: v for k, v in {
            'role_category': filters.role_category,
            'tech_stack': filters.tech_stack,
            'employment_type': filters.employment_type,
            'work_setup': filters.work_setup,
            'experience_level': filters.experience_level,
            'location': filters.location,
            'search': filters.search
        }.items() if v is not None
    }

    # Get filtered jobs with pagination
    jobs, total = await service.search_and_filter_jobs(
        filters=filter_dict,
        skip=filters.skip,
        limit=filters.limit
    )

    logger.info(
        "job_postings_listed",
        returned=len(jobs),
        total=total,
        skip=filters.skip,
        limit=filters.limit
    )

    return JobPostingListResponse(
        jobs=jobs,
        total=total,
        skip=filters.skip,
        limit=filters.limit
    )


@router.get("/{id}", response_model=JobPostingResponse)
async def get_job_posting(
    id: UUID,
    service: Annotated[JobPostingService, Depends(get_job_posting_service)]
) -> JobPostingResponse:
    """
    Get a single job posting by ID.

    Returns the complete job posting details including all fields.

    Args:
        id: UUID of the job posting
        service: JobPostingService instance (injected)

    Returns:
        JobPostingResponse with all job posting data

    Raises:
        HTTPException 404: If job posting not found
        HTTPException 422: If ID format is invalid (automatically by FastAPI)
    """
    logger.info("fetching_job_posting", job_id=str(id))

    job = await service.get_job_posting_by_id(id)

    logger.info("job_posting_fetched", job_id=str(id), title=job.title)

    return job
