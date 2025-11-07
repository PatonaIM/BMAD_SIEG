"""FastAPI dependencies for dependency injection."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.candidate import Candidate
from app.providers.openai_provider import OpenAIProvider
from app.repositories.application_repository import ApplicationRepository
from app.repositories.candidate import CandidateRepository
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.job_posting_repository import JobPostingRepository
from app.services.application_service import ApplicationService
from app.services.embedding_service import EmbeddingService
from app.services.explanation_cache import ExplanationCache
from app.services.explanation_service import ExplanationService
from app.services.interview_engine import InterviewEngine
from app.services.job_posting_service import JobPostingService
from app.services.profile_service import ProfileService

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> Candidate:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Authenticated candidate

    Raises:
        HTTPException: If token is invalid or candidate not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify and decode token
        user_id = verify_token(token)
    except JWTError as exc:
        raise credentials_exception from exc

    # Fetch candidate from database
    candidate_repo = CandidateRepository(db)
    candidate = await candidate_repo.get_by_id(user_id)

    if candidate is None:
        raise credentials_exception

    return candidate


async def get_candidate_repo(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> CandidateRepository:
    """
    Get candidate repository instance.

    Args:
        db: Database session

    Returns:
        CandidateRepository instance
    """
    return CandidateRepository(db)


async def get_application_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ApplicationRepository:
    """
    Get application repository instance.

    Args:
        db: Database session

    Returns:
        ApplicationRepository instance
    """
    return ApplicationRepository(db)


async def get_job_posting_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> JobPostingService:
    """
    Get job posting service instance.

    Args:
        db: Database session

    Returns:
        JobPostingService instance with repository
    """
    repo = JobPostingRepository(db)
    return JobPostingService(repo)


async def get_application_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ApplicationService:
    """
    Get application service instance.

    Factory dependency for ApplicationService that creates all required
    dependencies and injects them into the service.

    Args:
        db: Database session

    Returns:
        ApplicationService instance with all dependencies injected
    """
    app_repo = ApplicationRepository(db)
    job_repo = JobPostingRepository(db)
    interview_repo = InterviewRepository(db)

    # Initialize InterviewEngine with all required dependencies
    message_repo = InterviewMessageRepository(db)
    session_repo = InterviewSessionRepository(db)
    ai_provider = OpenAIProvider()
    interview_engine = InterviewEngine(
        ai_provider=ai_provider,
        session_repo=session_repo,
        message_repo=message_repo,
        interview_repo=interview_repo
    )

    return ApplicationService(app_repo, job_repo, interview_repo, interview_engine)


async def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProfileService:
    """
    Get profile service instance.

    Args:
        db: Database session

    Returns:
        ProfileService instance with candidate repository and embedding service
    """
    candidate_repo = CandidateRepository(db)
    job_repo = JobPostingRepository(db)
    embedding_service = EmbeddingService(candidate_repo, job_repo)
    explanation_cache = await get_explanation_cache()
    return ProfileService(candidate_repo, embedding_service, explanation_cache)


async def get_embedding_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> EmbeddingService:
    """
    Get embedding service instance.

    Args:
        db: Database session

    Returns:
        EmbeddingService instance with all dependencies
    """
    candidate_repo = CandidateRepository(db)
    job_repo = JobPostingRepository(db)
    return EmbeddingService(candidate_repo, job_repo)


async def get_matching_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> "MatchingRepository":
    """
    Get matching repository instance.

    Args:
        db: Database session

    Returns:
        MatchingRepository instance
    """
    from app.repositories.matching_repository import MatchingRepository
    return MatchingRepository(db)


async def get_matching_service(
    matching_repo: Annotated["MatchingRepository", Depends(get_matching_repository)],
    profile_service: Annotated[ProfileService, Depends(get_profile_service)]
) -> "MatchingService":
    """
    Get matching service instance.

    Args:
        matching_repo: Matching repository instance
        profile_service: Profile service instance

    Returns:
        MatchingService instance with all dependencies
    """
    from app.services.matching_service import MatchingService
    return MatchingService(matching_repo, profile_service)


# Singleton cache instance for explanation service
_explanation_cache: ExplanationCache | None = None


async def get_explanation_cache() -> ExplanationCache:
    """
    Get singleton explanation cache instance.
    
    Returns:
        ExplanationCache singleton instance
    """
    global _explanation_cache
    if _explanation_cache is None:
        _explanation_cache = ExplanationCache()
    return _explanation_cache


async def get_explanation_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ExplanationService:
    """
    Get explanation service instance.
    
    Factory dependency for ExplanationService that creates all required
    dependencies and injects them into the service.
    
    Args:
        db: Database session
    
    Returns:
        ExplanationService instance with all dependencies injected
    """
    openai_provider = OpenAIProvider()
    candidate_repo = CandidateRepository(db)
    job_repo = JobPostingRepository(db)
    cache = await get_explanation_cache()
    
    return ExplanationService(
        openai_provider=openai_provider,
        candidate_repo=candidate_repo,
        job_repo=job_repo,
        cache=cache
    )
