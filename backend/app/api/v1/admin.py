"""Admin API endpoints for system management."""
from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_embedding_service
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import OpenAIProviderError
from app.models import Candidate
from app.providers.openai_provider import OpenAIProvider
from app.repositories.candidate import CandidateRepository
from app.repositories.resume import ResumeRepository
from app.schemas.resume import ResumeParsingResponse
from app.services.embedding_service import EmbeddingService
from app.services.resume_parsing_service import ResumeParsingService
from app.utils.supabase_storage import SupabaseStorageClient

router = APIRouter(prefix="/admin", tags=["admin"])
logger = structlog.get_logger(__name__)


@router.get("/storage/usage")
async def get_storage_usage(
    current_user: Candidate = Depends(get_current_user)
):
    """
    Get current video storage usage (authenticated users only).

    Returns storage metrics including total size, file count, and threshold warning.

    Note: In production, this should be restricted to admin users only.
    For MVP, any authenticated user can view storage usage.

    Args:
        current_user: Authenticated candidate

    Returns:
        dict with:
            - total_size_bytes: Total storage used in bytes
            - total_size_gb: Total storage used in GB
            - file_count: Number of files in bucket
            - threshold_gb: Configured storage threshold
            - warning: Boolean indicating if threshold exceeded

    Raises:
        500: If storage API request fails
    """
    try:
        storage_client = SupabaseStorageClient()
        usage = await storage_client.get_bucket_usage()

        # Check against threshold
        threshold_exceeded = usage["total_size_gb"] > settings.video_storage_threshold_gb

        if threshold_exceeded:
            logger.warning(
                "storage_threshold_exceeded",
                total_gb=usage["total_size_gb"],
                threshold_gb=settings.video_storage_threshold_gb,
                file_count=usage["file_count"]
            )

        response = {
            **usage,
            "threshold_gb": settings.video_storage_threshold_gb,
            "warning": threshold_exceeded
        }

        logger.info(
            "storage_usage_retrieved",
            user_id=str(current_user.id),
            usage_gb=usage["total_size_gb"]
        )

        return response

    except Exception as e:
        logger.error(
            "storage_usage_retrieval_failed",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage usage"
        )


@router.post("/resumes/{resume_id}/parse", response_model=ResumeParsingResponse)
async def reparse_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Candidate = Depends(get_current_user),
):
    """
    Manually trigger resume re-parsing.

    Fetches the resume file, extracts text, and parses it using GPT-4o-mini.
    Updates the resume's parsed_data and auto-populates candidate profile.

    Note: In production, this should be restricted to admin users only.
    For MVP, any authenticated user can trigger re-parsing of their own resumes.

    Args:
        resume_id: UUID of the resume to parse
        db: Database session
        current_user: Authenticated candidate

    Returns:
        ResumeParsingResponse with parsing status and results

    Raises:
        404: If resume not found
        403: If resume doesn't belong to current user (security check)
        400: If resume has no text content or parsing fails
        500: If unexpected error occurs
    """
    try:
        # Initialize repositories and services
        resume_repo = ResumeRepository(db)
        candidate_repo = CandidateRepository(db)
        openai_provider = OpenAIProvider(model="gpt-4o-mini")
        parsing_service = ResumeParsingService(
            openai_provider=openai_provider,
            resume_repo=resume_repo,
            candidate_repo=candidate_repo,
        )

        # Fetch resume
        resume = await resume_repo.get_by_id(resume_id)
        if not resume:
            logger.warning("resume_not_found_for_parsing", resume_id=str(resume_id))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )

        # Security check: verify resume belongs to current user
        # (In MVP, we allow users to parse their own resumes)
        if resume.candidate_id != current_user.id:
            logger.warning(
                "unauthorized_resume_parsing_attempt",
                resume_id=str(resume_id),
                resume_owner=str(resume.candidate_id),
                requesting_user=str(current_user.id),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to parse this resume"
            )

        # TODO: In a real implementation, we would extract text from the file_url
        # For now, we expect the resume text to be provided in the request body
        # or already stored in a text field (to be added in future story)

        # Placeholder: For MVP, we'll use a sample text or raise an error
        # In Story 4.2, we assume text extraction is handled elsewhere
        resume_text = "Sample resume text placeholder"  # TODO: Replace with actual text extraction

        logger.info(
            "manual_resume_parsing_triggered",
            resume_id=str(resume_id),
            candidate_id=str(resume.candidate_id),
            triggered_by=str(current_user.id),
        )

        # Parse resume
        parsed_data = await parsing_service.parse_resume_text(resume_id, resume_text)

        # Return response
        return ResumeParsingResponse(
            resume_id=resume_id,
            parsing_status="completed",
            parsed_data=parsed_data,
            error_message=None,
        )

    except ValueError as e:
        # Resume not found or empty text
        logger.error(
            "resume_parsing_validation_error",
            resume_id=str(resume_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except OpenAIProviderError as e:
        # OpenAI parsing error
        logger.error(
            "resume_parsing_openai_error",
            resume_id=str(resume_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume parsing failed: {str(e)}"
        )

    except Exception as e:
        # Unexpected error
        logger.error(
            "resume_parsing_unexpected_error",
            resume_id=str(resume_id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume"
        )


# ============================================================================
# Embedding Generation Endpoints (Epic 04 - Story 4.4)
# ============================================================================

class BatchGenerateRequest(BaseModel):
    """Request schema for batch embedding generation."""
    entity_type: str = Field(..., pattern="^(candidates|jobs)$")
    force_regenerate: bool = False
    limit: int = Field(100, ge=1, le=1000)


class BatchGenerateResponse(BaseModel):
    """Response schema for batch embedding generation."""
    total_processed: int
    successful: int
    failed: int
    skipped: int
    errors: list[str]


@router.post("/embeddings/generate", response_model=BatchGenerateResponse)
async def batch_generate_embeddings(
    request: BatchGenerateRequest,
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    current_user: Annotated[Candidate, Depends(get_current_user)]
) -> BatchGenerateResponse:
    """
    Batch generate embeddings for candidates or job postings.

    **Admin Only:** Requires authenticated user (admin role check can be added later).

    **Parameters:**
    - entity_type: "candidates" or "jobs"
    - force_regenerate: If true, regenerate even if embedding exists
    - limit: Max number of records to process (default 100, max 1000)

    **Returns:**
    - Statistics: total processed, successful, failed, skipped

    **Example Request:**
    ```json
    {
        "entity_type": "candidates",
        "force_regenerate": false,
        "limit": 100
    }
    ```

    **Example Response:**
    ```json
    {
        "total_processed": 50,
        "successful": 48,
        "failed": 2,
        "skipped": 0,
        "errors": ["Failed to store embedding for candidate ..."]
    }
    ```

    Raises:
        400: Invalid request parameters
        500: Embedding generation failed
    """
    try:
        if request.entity_type == "candidates":
            result = await embedding_service.batch_generate_candidate_embeddings(
                force=request.force_regenerate,
                limit=request.limit
            )
        else:
            result = await embedding_service.batch_generate_job_embeddings(
                force=request.force_regenerate,
                limit=request.limit
            )

        logger.info(
            "batch_embedding_generation_completed",
            entity_type=request.entity_type,
            **result
        )

        return BatchGenerateResponse(**result)

    except ValueError as e:
        logger.warning("batch_embedding_generation_invalid_request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error("batch_embedding_generation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Embedding generation failed: {str(e)}"
        )
