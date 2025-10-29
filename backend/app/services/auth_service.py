"""Authentication service for candidate registration and login."""
import uuid

from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.models.candidate import Candidate
from app.repositories.candidate import CandidateRepository


class AuthService:
    """Service for authentication operations."""

    def __init__(self, candidate_repo: CandidateRepository):
        """
        Initialize auth service with repository.

        Args:
            candidate_repo: Candidate repository instance
        """
        self.candidate_repo = candidate_repo

    async def register_candidate(
        self, email: str, password: str, full_name: str, phone: str | None = None
    ) -> tuple[Candidate, str]:
        """
        Register a new candidate.

        Args:
            email: Candidate email address
            password: Plain text password
            full_name: Candidate full name
            phone: Optional phone number

        Returns:
            Tuple of (created candidate, JWT token)

        Raises:
            HTTPException: If email already exists
        """
        # Check if email already exists
        existing_candidate = await self.candidate_repo.get_by_email(email)
        if existing_candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hash_password(password)

        # Create candidate
        candidate = Candidate(
            id=uuid.uuid4(),
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            phone=phone,
            status="active"
        )

        candidate = await self.candidate_repo.create(candidate)

        # Generate JWT token
        token = create_access_token(candidate.id)

        return candidate, token

    async def login_candidate(self, email: str, password: str) -> tuple[Candidate, str]:
        """
        Authenticate a candidate and return JWT token.

        Args:
            email: Candidate email address
            password: Plain text password

        Returns:
            Tuple of (candidate, JWT token)

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find candidate by email
        candidate = await self.candidate_repo.get_by_email(email)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(password, candidate.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Generate JWT token
        token = create_access_token(candidate.id)

        return candidate, token
