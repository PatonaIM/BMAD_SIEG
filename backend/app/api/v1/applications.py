"""Application API routes."""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_application_service, get_current_user
from app.core.database import get_db
from app.models.application import Application
from app.models.candidate import Candidate
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationDetailResponse,
    ApplicationResponse,
)
from app.services.application_service import ApplicationService

logger = structlog.get_logger().bind(module="applications_api")

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreateRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    service: Annotated[ApplicationService, Depends(get_application_service)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ApplicationResponse:
    """
    Submit application to a job posting and start AI interview.

    Creates an application record linking the authenticated candidate to the specified
    job posting. Automatically creates and starts an AI interview customized to the
    job's role type. The interview is immediately linked to the application.

    **Authentication Required:** Bearer token (JWT)

    **Validation:**
    - Job posting must exist and be active
    - Candidate cannot have already applied to this job (409 if duplicate)

    **Automatic Actions:**
    - Creates new application with status='applied'
    - Creates new interview with role_type matching job posting
    - Links interview to application
    - Updates application status to 'interview_scheduled'

    **Returns:**
    - 201 Created: Application created successfully with linked interview
    - 400 Bad Request: Job posting is not active
    - 401 Unauthorized: Invalid or missing authentication token
    - 404 Not Found: Job posting does not exist
    - 409 Conflict: Already applied to this job posting

    **Example Request:**
    ```json
    {
        "job_posting_id": "123e4567-e89b-12d3-a456-426614174000"
    }
    ```

    **Example Response:**
    ```json
    {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
        "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
        "interview_id": "123e4567-e89b-12d3-a456-426614174003",
        "status": "interview_scheduled",
        "applied_at": "2025-11-04T10:30:00Z",
        "job_posting": {
            "title": "Senior React Developer",
            "company": "Tech Corp"
        }
    }
    ```
    """
    logger.info(
        "create_application_request",
        candidate_id=str(current_user.id),
        job_posting_id=str(data.job_posting_id)
    )

    try:
        # Service creates application + interview (no commit inside service)
        application, interview_session = await service.create_application(
            current_user.id,
            data.job_posting_id
        )

        # Commit transaction after service completes
        await db.commit()

        # Eagerly load relationships for response serialization
        stmt = (
            select(Application)
            .where(Application.id == application.id)
            .options(
                selectinload(Application.job_posting),
                selectinload(Application.interview)
            )
        )
        result = await db.execute(stmt)
        application = result.scalar_one()

        logger.info(
            "application_created_successfully",
            application_id=str(application.id),
            interview_id=str(application.interview_id),
            status=application.status
        )

        # Pydantic converts to ApplicationResponse automatically
        return application

    except HTTPException:
        # Re-raise HTTP exceptions from service
        raise
    except Exception as e:
        logger.error(
            "application_creation_error",
            candidate_id=str(current_user.id),
            job_posting_id=str(data.job_posting_id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        ) from e


@router.get("/me", response_model=list[ApplicationResponse])
async def get_my_applications(
    current_user: Annotated[Candidate, Depends(get_current_user)],
    service: Annotated[ApplicationService, Depends(get_application_service)],
    skip: int = 0,
    limit: int = 20
) -> list[ApplicationResponse]:
    """
    Get all applications submitted by the authenticated candidate.

    Returns a paginated list of applications with eager-loaded job posting
    and interview details.

    **Authentication Required:** Bearer token (JWT)

    **Query Parameters:**
    - skip: Number of records to skip for pagination (default: 0)
    - limit: Maximum number of records to return (default: 20, max: 100)

    **Returns:**
    - 200 OK: List of applications (may be empty)
    - 401 Unauthorized: Invalid or missing authentication token

    **Example Response:**
    ```json
    [
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
            "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
            "interview_id": "123e4567-e89b-12d3-a456-426614174003",
            "status": "interview_scheduled",
            "applied_at": "2025-11-04T10:30:00Z",
            "job_posting": {
                "title": "Senior React Developer",
                "company": "Tech Corp"
            },
            "interview": {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "status": "in_progress",
                "role_type": "react"
            }
        }
    ]
    ```
    """
    logger.info(
        "get_my_applications_request",
        candidate_id=str(current_user.id),
        skip=skip,
        limit=limit
    )

    # Limit max to 100 to prevent large queries
    if limit > 100:
        limit = 100

    applications = await service.get_candidate_applications(
        current_user.id,
        skip=skip,
        limit=limit
    )

    logger.info(
        "my_applications_fetched",
        candidate_id=str(current_user.id),
        count=len(applications)
    )

    return applications


@router.get("/{id}", response_model=ApplicationDetailResponse)
async def get_application(
    id: UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    service: Annotated[ApplicationService, Depends(get_application_service)]
) -> ApplicationDetailResponse:
    """
    Get details of a specific application by ID.

    Returns full application details including job posting and interview information.
    Only accessible by the candidate who owns the application.

    **Authentication Required:** Bearer token (JWT)

    **Authorization:** Candidate can only access their own applications

    **Returns:**
    - 200 OK: Application details
    - 401 Unauthorized: Invalid or missing authentication token
    - 403 Forbidden: Application belongs to another candidate
    - 404 Not Found: Application not found

    **Example Response:**
    ```json
    {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "candidate_id": "123e4567-e89b-12d3-a456-426614174002",
        "job_posting_id": "123e4567-e89b-12d3-a456-426614174000",
        "interview_id": "123e4567-e89b-12d3-a456-426614174003",
        "status": "interview_scheduled",
        "applied_at": "2025-11-04T10:30:00Z",
        "job_posting": {
            "title": "Senior React Developer",
            "company": "Tech Corp",
            "role_category": "engineering",
            "tech_stack": "react"
        },
        "interview": {
            "id": "123e4567-e89b-12d3-a456-426614174003",
            "status": "in_progress",
            "role_type": "react"
        }
    }
    ```
    """
    logger.info(
        "get_application_request",
        application_id=str(id),
        candidate_id=str(current_user.id)
    )

    # Service handles authorization check
    application = await service.get_application_by_id(id, current_user.id)

    logger.info(
        "application_fetched",
        application_id=str(id),
        candidate_id=str(current_user.id)
    )

    return application
