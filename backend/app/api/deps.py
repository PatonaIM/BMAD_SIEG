"""FastAPI dependencies for dependency injection."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.candidate import Candidate
from app.repositories.candidate import CandidateRepository

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
