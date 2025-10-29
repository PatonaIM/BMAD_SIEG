"""Interview API routes."""
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.schemas.interview import InterviewResponse, InterviewStartRequest

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    data: InterviewStartRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> InterviewResponse:
    """
    Start a new interview session.

    Args:
        data: Interview start request (role_type, resume_id)
        current_user: Authenticated candidate
        db: Database session

    Returns:
        Created interview with status "scheduled"
    """
    # Create interview record
    interview = Interview(
        id=uuid.uuid4(),
        candidate_id=current_user.id,
        resume_id=data.resume_id,
        role_type=data.role_type,
        status="scheduled",
        total_tokens_used=0
    )

    db.add(interview)
    await db.flush()
    await db.refresh(interview)

    # Create associated interview session
    interview_session = InterviewSession(
        id=uuid.uuid4(),
        interview_id=interview.id,
        current_difficulty_level="warmup",
        questions_asked_count=0
    )

    db.add(interview_session)
    await db.commit()

    return interview
