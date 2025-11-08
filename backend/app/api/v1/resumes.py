"""Resume upload and analysis API endpoints."""
from uuid import UUID

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.candidate import Candidate
from app.providers.openai_provider import OpenAIProvider
from app.repositories.resume import ResumeRepository
from app.repositories.resume_analysis import ResumeAnalysisRepository
from app.schemas.resume import ResumeAnalysisResponse, ResumeResponse, ResumeUploadResponse
from app.services.resume_analysis_service import ResumeAnalysisService
from app.services.resume_upload_service import ResumeUploadService
from app.utils.pdf_extractor import PDFTextExtractor
from app.utils.prompt_loader import PromptTemplateManager
from app.utils.supabase_storage import SupabaseStorageClient

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


# Dependency injection helpers
def get_resume_upload_service(db: AsyncSession = Depends(get_db)) -> ResumeUploadService:
    """Get ResumeUploadService instance with dependencies."""
    storage_client = SupabaseStorageClient()
    resume_repo = ResumeRepository(db)
    pdf_extractor = PDFTextExtractor()
    return ResumeUploadService(storage_client, resume_repo, pdf_extractor)


def get_resume_analysis_service(db: AsyncSession = Depends(get_db)) -> ResumeAnalysisService:
    """Get ResumeAnalysisService instance with dependencies."""
    openai_provider = OpenAIProvider(model="gpt-4o-mini")
    analysis_repo = ResumeAnalysisRepository(db)
    prompt_manager = PromptTemplateManager()
    return ResumeAnalysisService(openai_provider, analysis_repo, prompt_manager)


async def trigger_analysis_background(
    resume_id: UUID, resume_text: str
) -> None:
    """
    Background task to analyze resume after upload.

    Creates its own DB session to avoid session issues with FastAPI request lifecycle.

    Args:
        resume_id: UUID of uploaded resume
        resume_text: Extracted resume text
    """
    from app.api.deps import get_db
    from app.providers.openai_provider import OpenAIProvider
    from app.repositories.resume_analysis import ResumeAnalysisRepository
    from app.utils.prompt_loader import PromptTemplateManager
    from app.services.resume_analysis_service import ResumeAnalysisService
    from app.core.config import settings
    
    try:
        # Create new DB session for background task
        async for db in get_db():
            # Initialize dependencies
            openai_provider = OpenAIProvider(
                api_key=settings.openai_api_key.get_secret_value(),
                model="gpt-4o-mini"
            )
            analysis_repo = ResumeAnalysisRepository(db)
            prompt_manager = PromptTemplateManager()
            
            # Create service
            analysis_service = ResumeAnalysisService(
                openai_provider=openai_provider,
                analysis_repo=analysis_repo,
                prompt_manager=prompt_manager
            )
            
            # Run analysis
            await analysis_service.analyze_resume(resume_id, resume_text)
            
            # Commit the transaction
            await db.commit()
            
            logger.info("background_analysis_completed", resume_id=str(resume_id))
            break  # Exit after first iteration
            
    except Exception as e:
        logger.error(
            "background_analysis_failed",
            resume_id=str(resume_id),
            error=str(e),
        )


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: Candidate = Depends(get_current_user),
    upload_service: ResumeUploadService = Depends(get_resume_upload_service),
) -> ResumeUploadResponse:
    """
    Upload resume PDF and trigger AI analysis.

    This endpoint:
    1. Validates file (PDF, max 5MB)
    2. Deactivates previous active resumes
    3. Uploads to Supabase Storage
    4. Extracts text from PDF
    5. Triggers analysis in background (non-blocking)
    6. Returns resume metadata immediately

    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded PDF file
        current_user: Authenticated candidate
        upload_service: Service for handling uploads

    Returns:
        ResumeUploadResponse with resume metadata

    Raises:
        400: Invalid file type or size
        500: Upload or extraction failed
    """
    logger.info(
        "resume_upload_request",
        candidate_id=str(current_user.id),
        filename=file.filename,
    )

    try:
        # Upload resume and extract text
        resume, extracted_text = await upload_service.upload_resume(current_user.id, file)

        # Trigger analysis in background (non-blocking)
        background_tasks.add_task(
            trigger_analysis_background, resume.id, extracted_text
        )

        logger.info(
            "resume_upload_success",
            candidate_id=str(current_user.id),
            resume_id=str(resume.id),
        )

        return ResumeUploadResponse.model_validate(resume)

    except ValueError as e:
        logger.warning(
            "resume_upload_validation_failed",
            candidate_id=str(current_user.id),
            error=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        logger.error(
            "resume_upload_failed",
            candidate_id=str(current_user.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resume upload failed",
        )


@router.get("", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ResumeResponse]:
    """
    Get all resumes for current candidate.

    Resumes are ordered by uploaded_at DESC (newest first).

    Args:
        current_user: Authenticated candidate
        db: Database session

    Returns:
        List of ResumeResponse
    """
    resume_repo = ResumeRepository(db)
    resumes = await resume_repo.get_by_candidate_id(current_user.id)

    logger.debug(
        "resumes_listed",
        candidate_id=str(current_user.id),
        count=len(resumes),
    )

    return [ResumeResponse.model_validate(r) for r in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """
    Get single resume details.

    Args:
        resume_id: UUID of the resume
        current_user: Authenticated candidate
        db: Database session

    Returns:
        ResumeResponse

    Raises:
        404: Resume not found or doesn't belong to candidate
    """
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(resume_id)

    if not resume or resume.candidate_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    return ResumeResponse.model_validate(resume)


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeAnalysisResponse:
    """
    Get AI analysis for resume.

    Returns the most recent analysis. If no analysis exists yet (still processing),
    returns 404.

    Args:
        resume_id: UUID of the resume
        current_user: Authenticated candidate
        db: Database session

    Returns:
        ResumeAnalysisResponse

    Raises:
        404: Resume not found, doesn't belong to candidate, or analysis not ready
    """
    # Verify resume belongs to candidate
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(resume_id)

    if not resume or resume.candidate_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    # Get latest analysis
    analysis_repo = ResumeAnalysisRepository(db)
    analysis = await analysis_repo.get_latest_by_resume_id(resume_id)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not ready yet. Please check back in a moment.",
        )

    return ResumeAnalysisResponse.model_validate(analysis)


@router.post("/{resume_id}/activate", response_model=ResumeResponse)
async def activate_resume(
    resume_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """
    Set resume as active (deactivates others).

    Only one resume can be active at a time per candidate.

    Args:
        resume_id: UUID of the resume to activate
        current_user: Authenticated candidate
        db: Database session

    Returns:
        ResumeResponse with updated resume

    Raises:
        404: Resume not found or doesn't belong to candidate
    """
    resume_repo = ResumeRepository(db)

    try:
        resume = await resume_repo.set_active(resume_id, current_user.id)

        logger.info(
            "resume_activated",
            candidate_id=str(current_user.id),
            resume_id=str(resume_id),
        )

        return ResumeResponse.model_validate(resume)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    upload_service: ResumeUploadService = Depends(get_resume_upload_service),
) -> None:
    """
    Delete resume from database and storage.

    Also deletes all associated analyses (cascade).

    Args:
        resume_id: UUID of the resume to delete
        current_user: Authenticated candidate
        upload_service: Service for handling deletion

    Raises:
        404: Resume not found or doesn't belong to candidate
    """
    try:
        await upload_service.delete_resume(resume_id, current_user.id)

        logger.info(
            "resume_deleted_via_api",
            candidate_id=str(current_user.id),
            resume_id=str(resume_id),
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: UUID,
    current_user: Candidate = Depends(get_current_user),
    upload_service: ResumeUploadService = Depends(get_resume_upload_service),
) -> dict:
    """
    Get signed URL for resume download.

    Returns a temporary signed URL that expires in 24 hours.

    Args:
        resume_id: UUID of the resume
        current_user: Authenticated candidate
        upload_service: Service for generating signed URLs

    Returns:
        dict with signed_url

    Raises:
        404: Resume not found or doesn't belong to candidate
    """
    try:
        signed_url = await upload_service.generate_signed_url(resume_id, current_user.id)

        return {"signed_url": signed_url, "expires_in": 86400}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
