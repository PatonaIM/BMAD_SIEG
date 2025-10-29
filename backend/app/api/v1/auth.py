"""Authentication API routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.candidate import CandidateRepository
from app.schemas.auth import (
    AuthTokenResponse,
    CandidateLoginRequest,
    CandidateRegisterRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: CandidateRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthTokenResponse:
    """
    Register a new candidate.

    Args:
        data: Registration data (email, password, full_name, phone)
        db: Database session

    Returns:
        JWT token and candidate information

    Raises:
        HTTPException 400: If email already exists
    """
    candidate_repo = CandidateRepository(db)
    auth_service = AuthService(candidate_repo)

    candidate, token = await auth_service.register_candidate(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        phone=data.phone
    )

    await db.commit()

    return AuthTokenResponse(
        token=token,
        candidate_id=candidate.id,
        email=candidate.email,
        full_name=candidate.full_name
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login(
    data: CandidateLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthTokenResponse:
    """
    Authenticate a candidate and return JWT token.

    Args:
        data: Login credentials (email, password)
        db: Database session

    Returns:
        JWT token and candidate information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    candidate_repo = CandidateRepository(db)
    auth_service = AuthService(candidate_repo)

    candidate, token = await auth_service.login_candidate(
        email=data.email,
        password=data.password
    )

    return AuthTokenResponse(
        token=token,
        candidate_id=candidate.id,
        email=candidate.email,
        full_name=candidate.full_name
    )
