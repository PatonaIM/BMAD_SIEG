"""Interview API routes."""
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import (
    InterviewNotFoundException,
    InterviewCompletedException,
    OpenAIRateLimitException,
)
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.interview_session import InterviewSession
from app.models.interview_message import InterviewMessage
from app.schemas.interview import (
    InterviewResponse,
    InterviewStartRequest,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.interview_engine import InterviewEngine
from app.providers.openai_provider import OpenAIProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.repositories.interview_message import InterviewMessageRepository

logger = structlog.get_logger().bind(module="interviews_api")

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/start", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    data: InterviewStartRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> InterviewResponse:
    """
    Start a new interview session and generate the first AI question.

    Args:
        data: Interview start request (role_type, resume_id)
        current_user: Authenticated candidate
        db: Database session

    Returns:
        Created interview with status "in_progress" and first AI question
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "start_interview_request",
        correlation_id=correlation_id,
        candidate_id=str(current_user.id),
        role_type=data.role_type
    )
    
    # Create interview record with in_progress status
    interview = Interview(
        id=uuid.uuid4(),
        candidate_id=current_user.id,
        resume_id=data.resume_id,
        role_type=data.role_type,
        status="in_progress",  # Changed from "scheduled"
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
        questions_asked_count=0,
        skill_boundaries_identified={},
        progression_state={
            "phase_history": [],
            "response_quality_history": [],
            "skills_assessed": [],
            "skills_pending": [],
            "boundary_detections": []
        },
        conversation_memory={"messages": [], "metadata": {}},
        last_activity_at=datetime.utcnow()
    )

    db.add(interview_session)
    await db.flush()
    
    # Generate first AI question
    try:
        # Initialize repositories and services
        message_repo = InterviewMessageRepository(db)
        session_repo = InterviewSessionRepository(db)
        ai_provider = OpenAIProvider()
        interview_engine = InterviewEngine(
            ai_provider=ai_provider,
            session_repo=session_repo,
            message_repo=message_repo
        )
        
        # Generate the first question using the correct signature
        first_question = await interview_engine.assessment_engine.generate_next_question(
            session=interview_session,
            role_type=data.role_type
        )
        
        # Create AI message record for first question
        ai_message = InterviewMessage(
            id=uuid.uuid4(),
            interview_id=interview.id,
            session_id=interview_session.id,
            sequence_number=1,
            message_type="ai_question",
            content_text=first_question["question"],
            created_at=datetime.utcnow()
        )
        
        db.add(ai_message)
        
        # Update session with first question
        interview_session.questions_asked_count = 1
        interview_session.conversation_memory = {
            "messages": [
                {
                    "role": "assistant",
                    "content": first_question["question"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "metadata": {
                "message_count": 1,
                "token_count": 0
            }
        }
        
        await db.commit()
        
        logger.info(
            "interview_started_successfully",
            correlation_id=correlation_id,
            interview_id=str(interview.id),
            session_id=str(interview_session.id)
        )
        
    except Exception as e:
        logger.error(
            "failed_to_generate_first_question",
            correlation_id=correlation_id,
            interview_id=str(interview.id),
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start interview. Please try again."
        )

    return interview


@router.post("/{interview_id}/messages", response_model=SendMessageResponse)
async def send_interview_message(
    interview_id: uuid.UUID,
    request: SendMessageRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> SendMessageResponse:
    """
    Submit candidate response and receive next AI question.
    
    Processes the candidate's message, generates an AI response using
    the interview engine, and returns the next question with progression data.

    Args:
        interview_id: Active interview UUID
        request: Message request with candidate's response text
        current_user: Authenticated candidate
        db: Database session

    Returns:
        SendMessageResponse with AI question and session state

    Raises:
        HTTPException 404: Interview not found
        HTTPException 403: Interview doesn't belong to candidate
        HTTPException 400: Interview not in progress
        HTTPException 429: OpenAI rate limit exceeded
        HTTPException 500: Internal server error
    """
    correlation_id = str(uuid.uuid4())
    
    logger.info(
        "message_request_received",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id),
        message_length=len(request.message_text)
    )
    
    try:
        # Initialize repositories
        interview_repo = InterviewRepository(db)
        session_repo = InterviewSessionRepository(db)
        message_repo = InterviewMessageRepository(db)
        
        # Load interview with session
        interview = await interview_repo.get_by_id_with_session(interview_id)
        
        if not interview:
            logger.warning(
                "interview_not_found",
                correlation_id=correlation_id,
                interview_id=str(interview_id)
            )
            raise InterviewNotFoundException(f"Interview {interview_id} not found")
        
        # Verify ownership
        if interview.candidate_id != current_user.id:
            logger.warning(
                "unauthorized_interview_access",
                correlation_id=correlation_id,
                interview_id=str(interview_id),
                candidate_id=str(current_user.id),
                owner_id=str(interview.candidate_id)
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this interview"
            )
        
        # Verify interview is in progress
        if interview.status == "completed":
            raise InterviewCompletedException(
                f"Interview {interview_id} is already completed"
            )
        elif interview.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interview status must be 'in_progress', got '{interview.status}'"
            )
        
        # Initialize AI provider and interview engine
        ai_provider = OpenAIProvider()
        interview_engine = InterviewEngine(
            ai_provider=ai_provider,
            session_repo=session_repo,
            message_repo=message_repo
        )
        
        # Process candidate response
        result = await interview_engine.process_candidate_response(
            interview_id=interview_id,
            session_id=interview.session.id,
            response_text=request.message_text,
            role_type=interview.role_type
        )
        
        # Commit all changes
        await db.commit()
        
        logger.info(
            "message_processed_successfully",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            question_number=result["question_number"],
            tokens_used=result.get("tokens_used", 0)
        )
        
        # Return response
        return SendMessageResponse(
            message_id=result["message_id"],
            ai_response=result["ai_response"],
            question_number=result["question_number"],
            total_questions=result["total_questions"],
            session_state=result["session_state"]
        )
        
    except InterviewNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    except InterviewCompletedException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except OpenAIRateLimitException as e:
        logger.error(
            "openai_rate_limit_exceeded",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI service rate limit exceeded. Please try again in a moment.",
            headers={"Retry-After": "60"}
        )
    except Exception as e:
        logger.error(
            "message_processing_error",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.get("/{interview_id}/status")
async def get_interview_status(
    interview_id: uuid.UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """
    Get interview status and progress information.
    
    Used by frontend for session recovery and progress tracking.

    Args:
        interview_id: Interview UUID
        current_user: Authenticated candidate
        db: Database session

    Returns:
        Interview status, question count, last activity, difficulty level

    Raises:
        HTTPException 404: Interview not found
        HTTPException 403: Not authorized
    """
    interview_repo = InterviewRepository(db)
    session_repo = InterviewSessionRepository(db)
    
    # Load interview
    interview = await interview_repo.get_by_id(interview_id)
    
    if not interview:
        logger.warning(
            "status_check_interview_not_found",
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Verify ownership
    if interview.candidate_id != current_user.id:
        logger.warning(
            "unauthorized_status_check",
            interview_id=str(interview_id),
            candidate_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this interview"
        )
    
    # Get session if exists
    session = await session_repo.get_by_interview_id(interview_id)
    
    return {
        "interview_id": str(interview_id),
        "status": interview.status,
        "role_type": interview.role_type,
        "started_at": interview.started_at.isoformat() if interview.started_at else None,
        "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
        "questions_asked": session.questions_asked_count if session else 0,
        "current_difficulty": session.current_difficulty_level if session else "warmup",
        "last_activity_at": session.last_activity_at.isoformat() if session and session.last_activity_at else None,
        "skill_boundaries": session.skill_boundaries_identified if session else {},
    }


@router.get("/{interview_id}/messages")
async def get_interview_messages(
    interview_id: uuid.UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
    min_sequence: int | None = None,
    max_sequence: int | None = None
) -> dict:
    """
    Get conversation history for an interview.
    
    Returns paginated list of messages with optional sequence filtering.

    Args:
        interview_id: Interview UUID
        current_user: Authenticated candidate
        db: Database session
        skip: Number of messages to skip (pagination)
        limit: Maximum messages to return (max 100)
        min_sequence: Optional minimum sequence number filter
        max_sequence: Optional maximum sequence number filter

    Returns:
        List of messages with pagination info

    Raises:
        HTTPException 404: Interview not found
        HTTPException 403: Not authorized
    """
    interview_repo = InterviewRepository(db)
    message_repo = InterviewMessageRepository(db)
    
    # Load interview
    interview = await interview_repo.get_by_id(interview_id)
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Verify ownership
    if interview.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this interview"
        )
    
    # Limit to reasonable max
    limit = min(limit, 100)
    
    # Get all messages for the interview
    all_messages = await message_repo.get_by_interview_id(interview_id)
    
    # Apply sequence filters if provided
    if min_sequence is not None:
        all_messages = [m for m in all_messages if m.sequence_number >= min_sequence]
    if max_sequence is not None:
        all_messages = [m for m in all_messages if m.sequence_number <= max_sequence]
    
    # Apply pagination
    total_count = len(all_messages)
    messages = all_messages[skip:skip + limit]
    
    return {
        "interview_id": str(interview_id),
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "messages": [
            {
                "id": str(msg.id),
                "sequence_number": msg.sequence_number,
                "message_type": msg.message_type,
                "content_text": msg.content_text,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]
    }
