"""Interview API routes."""
import uuid
from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_application_repository, get_current_user
from app.core.database import get_db
from app.core.exceptions import (
    InterviewCompletedException,
    InterviewNotFoundException,
    OpenAIRateLimitException,
)
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.models.interview_message import InterviewMessage
from app.models.interview_session import InterviewSession
from app.providers.openai_provider import OpenAIProvider
from app.repositories.application_repository import ApplicationRepository
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.schemas.interview import (
    InterviewCompleteResponse,
    InterviewResponse,
    InterviewStartRequest,
    InterviewTranscriptResponse,
    SendMessageRequest,
    SendMessageResponse,
    TechCheckRequest,
    TechCheckResponse,
    TranscriptMessage,
    VideoChunkUploadResponse,
    VideoConsentRequest,
    VideoConsentResponse,
)
from app.services.interview_engine import InterviewEngine

logger = structlog.get_logger().bind(module="interviews_api")

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _map_role_type(role_type_raw: str) -> str:
    """
    Map tech_stack or role_category to valid interview role_type enum.
    
    Uses the same expanded mapping as ApplicationService (50+ mappings)
    to support both technical and non-technical roles.
    
    Args:
        role_type_raw: Raw tech_stack or role_category string
    
    Returns:
        Mapped role_type enum value (react|python|javascript|fullstack)
    """
    role_type_mapping = {
        # Technical mappings
        "react": "react",
        "python": "python",
        "javascript": "javascript",
        "typescript": "javascript",
        "go": "python",
        "rust": "python",
        "java": "python",
        "csharp": "python",
        "c#": "python",
        "dotnet": "python",
        ".net": "python",
        "php": "python",
        "node": "javascript",
        "nodejs": "javascript",
        "node.js": "javascript",
        "data": "python",
        "data_engineering": "python",
        "data engineering": "python",
        "devops": "python",
        "qa": "javascript",
        "qa_automation": "javascript",
        "quality_assurance": "javascript",
        "playwright": "javascript",
        "cypress": "javascript",

        # Non-technical role mappings
        "sales": "fullstack",
        "account_manager": "fullstack",
        "account manager": "fullstack",
        "business_development": "fullstack",
        "business development": "fullstack",
        "support": "fullstack",
        "customer_service": "fullstack",
        "customer service": "fullstack",
        "customer_success": "fullstack",
        "customer success": "fullstack",
        "product": "fullstack",
        "product_manager": "fullstack",
        "product manager": "fullstack",
        "design": "fullstack",
        "ux": "fullstack",
        "ui": "fullstack",
        "ux/ui": "fullstack",
        "marketing": "fullstack",
        "operations": "fullstack",
        "management": "fullstack",

        # Default
        "fullstack": "fullstack",
        "full-stack": "fullstack",
        "full stack": "fullstack",
    }
    return role_type_mapping.get(role_type_raw.lower(), "fullstack")


@router.post("/start", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    data: InterviewStartRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    app_repo: Annotated[ApplicationRepository, Depends(get_application_repository)]
) -> InterviewResponse:
    """
    Start a new interview session and generate the first AI question.
    
    Supports two modes:
    1. Standalone interview: Provide role_type for practice/standalone interview
    2. Job-linked interview: Provide application_id to link interview to job posting
       (role_type automatically derived from job's tech_stack)
    
    Job-linked interviews automatically inject job context into AI prompts
    for customized, role-specific questions.

    Args:
        data: Interview start request (role_type OR application_id, optional resume_id)
        current_user: Authenticated candidate
        db: Database session
        app_repo: Application repository for fetching job context

    Returns:
        Created interview with status "in_progress" and first AI question
        
    Raises:
        HTTPException 400: Neither role_type nor application_id provided
        HTTPException 403: Attempting to use another candidate's application
        HTTPException 404: Application or job posting not found
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "start_interview_request",
        correlation_id=correlation_id,
        candidate_id=str(current_user.id),
        role_type=data.role_type,
        application_id=str(data.application_id) if data.application_id else None
    )

    # Determine role_type and job_posting_id
    job_posting_id = None
    final_role_type = data.role_type

    if data.application_id:
        # Fetch application with eager-loaded job_posting
        application = await app_repo.get_by_id(data.application_id)

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {data.application_id} not found"
            )

        # Authorization: Verify application belongs to current user
        if application.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this application"
            )

        # Extract job context via eager-loaded relationship
        job_posting = application.job_posting
        if not job_posting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting not found for application {data.application_id}"
            )

        job_posting_id = job_posting.id

        # Use existing role mapping from ApplicationService (Story 3.13)
        # Priority: tech_stack first, then role_category, then default
        role_type_raw = (
            job_posting.tech_stack or
            str(job_posting.role_category) or
            "fullstack"
        )
        final_role_type = _map_role_type(role_type_raw)

        logger.info(
            "interview_start_with_job_context",
            correlation_id=correlation_id,
            application_id=str(data.application_id),
            job_posting_id=str(job_posting_id),
            tech_stack=job_posting.tech_stack,
            role_category=str(job_posting.role_category),
            mapped_role_type=final_role_type
        )

    elif not data.role_type:
        # Neither application_id nor role_type provided
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either application_id or role_type must be provided"
        )

    # Create interview record with in_progress status
    interview = Interview(
        id=uuid.uuid4(),
        candidate_id=current_user.id,
        resume_id=data.resume_id,
        role_type=final_role_type,
        job_posting_id=job_posting_id,  # Set FK (Story 3.13 column)
        status="in_progress",
        started_at=datetime.utcnow(),  # Set start time for accurate duration tracking
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
            session_id=str(interview_session.id),
            role_type=final_role_type,
            has_job_context=bool(job_posting_id)
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

        # Check if interview should be completed
        if result.get("interview_complete", False):
            logger.info(
                "interview_auto_completing",
                correlation_id=correlation_id,
                interview_id=str(interview_id),
                questions_asked=result["question_number"]
            )

            # Update interview status to completed
            interview.status = "completed"
            interview.completed_at = datetime.utcnow()

            # Calculate duration if started_at exists
            if interview.started_at:
                duration = (interview.completed_at - interview.started_at).total_seconds()
                interview.duration_seconds = int(duration)

            db.add(interview)

        # Commit all changes
        await db.commit()

        logger.info(
            "message_processed_successfully",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            question_number=result["question_number"],
            tokens_used=result.get("tokens_used", 0),
            interview_complete=result.get("interview_complete", False)
        )

        # Return response
        return SendMessageResponse(
            message_id=result["message_id"],
            ai_response=result["ai_response"],
            question_number=result["question_number"],
            total_questions=result["total_questions"],
            session_state=result["session_state"],
            interview_complete=result.get("interview_complete", False)
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


@router.post("/{interview_id}/complete", response_model=InterviewCompleteResponse)
async def complete_interview(
    interview_id: uuid.UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> InterviewCompleteResponse:
    """
    Mark an interview as completed and calculate final metrics.
    
    Updates the interview status to 'completed', calculates total duration,
    and returns completion summary with statistics.

    Args:
        interview_id: Interview UUID to complete
        current_user: Authenticated candidate
        db: Database session

    Returns:
        InterviewCompleteResponse with completion data

    Raises:
        HTTPException 404: Interview not found
        HTTPException 403: Not authorized to complete this interview
        HTTPException 400: Interview already completed or invalid status
        HTTPException 500: Internal server error
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "complete_interview_request",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id)
    )

    # Initialize repositories
    interview_repo = InterviewRepository(db)
    session_repo = InterviewSessionRepository(db)
    message_repo = InterviewMessageRepository(db)

    # Load interview
    interview = await interview_repo.get_by_id(interview_id)

    if not interview:
        logger.warning(
            "interview_not_found",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Verify ownership
    if interview.candidate_id != current_user.id:
        logger.warning(
            "unauthorized_completion_attempt",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            candidate_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to complete this interview"
        )

    # Check if already completed
    if interview.status == "completed":
        logger.warning(
            "interview_already_completed",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview has already been completed"
        )

    try:
        logger.info(
            "initializing_interview_engine",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        
        # Initialize AI provider and interview engine
        ai_provider = OpenAIProvider()
        interview_engine = InterviewEngine(
            ai_provider=ai_provider,
            session_repo=session_repo,
            message_repo=message_repo,
            interview_repo=interview_repo
        )

        logger.info(
            "calling_complete_interview_method",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        
        # Complete the interview
        result = await interview_engine.complete_interview(interview_id)

        logger.info(
            "committing_completion_transaction",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        
        await db.commit()

        logger.info(
            "interview_completed_successfully",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            duration_seconds=result["duration_seconds"],
            questions_answered=result["questions_answered"]
        )

        return InterviewCompleteResponse(**result)

    except InterviewCompletedException as e:
        logger.warning(
            "interview_already_completed",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InterviewNotFoundException as e:
        logger.error(
            "interview_not_found_during_completion",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "interview_completion_failed",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            error=str(e)
        )
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete interview. Please try again."
        )


@router.get("/{interview_id}/transcript", response_model=InterviewTranscriptResponse)
async def get_interview_transcript(
    interview_id: uuid.UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
) -> InterviewTranscriptResponse:
    """
    Get complete interview transcript with all messages.
    
    Returns chronologically ordered messages from the interview conversation,
    with pagination support for long transcripts.

    Args:
        interview_id: Interview UUID
        current_user: Authenticated candidate
        db: Database session
        skip: Number of messages to skip (default: 0)
        limit: Maximum messages to return (default: 100, max: 100)

    Returns:
        InterviewTranscriptResponse with interview details and messages

    Raises:
        HTTPException 404: Interview not found
        HTTPException 403: Not authorized to access this transcript
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "get_transcript_request",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id)
    )

    # Initialize repositories
    interview_repo = InterviewRepository(db)
    message_repo = InterviewMessageRepository(db)

    # Load interview
    interview = await interview_repo.get_by_id(interview_id)

    if not interview:
        logger.warning(
            "interview_not_found_for_transcript",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Verify ownership
    if interview.candidate_id != current_user.id:
        logger.warning(
            "unauthorized_transcript_access",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            candidate_id=str(current_user.id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transcript"
        )

    # Get all messages
    all_messages = await message_repo.get_by_interview_id(interview_id)

    # Apply pagination with limit cap
    limit = min(limit, 100)
    paginated_messages = all_messages[skip:skip + limit]

    # Convert to TranscriptMessage schema
    transcript_messages = [
        TranscriptMessage(
            sequence_number=msg.sequence_number,
            message_type=msg.message_type,
            content_text=msg.content_text,
            created_at=msg.created_at,
            audio_url=msg.audio_url if hasattr(msg, 'audio_url') else None
        )
        for msg in paginated_messages
    ]

    logger.info(
        "transcript_retrieved_successfully",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        message_count=len(transcript_messages),
        total_messages=len(all_messages)
    )

    return InterviewTranscriptResponse(
        interview_id=interview_id,
        started_at=interview.started_at or datetime.utcnow(),
        completed_at=interview.completed_at,
        duration_seconds=interview.duration_seconds,
        messages=transcript_messages
    )


@router.post("/{interview_id}/tech-check", response_model=TechCheckResponse, status_code=status.HTTP_201_CREATED)
async def submit_tech_check_results(
    interview_id: uuid.UUID,
    request: TechCheckRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> TechCheckResponse:
    """
    Store tech check results for troubleshooting.
    
    Saves audio and camera test results to interviews.tech_check_metadata JSONB field.
    
    Args:
        interview_id: UUID of the interview
        request: Tech check results data
        current_user: Authenticated candidate
        db: Database session
        
    Returns:
        Success status and message
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "tech_check_submission",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id),
        audio_passed=request.audio_test_passed,
        camera_passed=request.camera_test_passed
    )

    interview_repo = InterviewRepository(db)

    # Get interview
    interview = await interview_repo.get_by_id(interview_id)
    if not interview:
        logger.warning(
            "tech_check_interview_not_found",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )

    # Verify ownership
    if interview.candidate_id != current_user.id:
        logger.warning(
            "unauthorized_tech_check_access",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            candidate_id=str(current_user.id),
            interview_candidate_id=str(interview.candidate_id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    # Store tech check metadata
    interview.tech_check_metadata = {
        "audio": {
            "permission_granted": request.audio_test_passed,
            "test_passed": request.audio_test_passed,
            "audio_level_detected": request.audio_metadata.get("level", 0),
            "test_timestamp": datetime.utcnow().isoformat(),
            "device_name": request.audio_metadata.get("device_name"),
            "browser_info": request.browser_info
        },
        "camera": {
            "permission_granted": request.camera_test_passed,
            "test_passed": request.camera_test_passed,
            "resolution_detected": request.camera_metadata.get("resolution"),
            "test_timestamp": datetime.utcnow().isoformat(),
            "device_name": request.camera_metadata.get("device_name"),
            "browser_info": request.browser_info
        }
    }

    await db.commit()

    logger.info(
        "tech_check_results_stored",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        audio_passed=request.audio_test_passed,
        camera_passed=request.camera_test_passed
    )

    return TechCheckResponse(
        success=True,
        message="Tech check results saved successfully"
    )


@router.post("/{interview_id}/video/upload", response_model=VideoChunkUploadResponse)
async def upload_video_chunk(
    interview_id: uuid.UUID,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    chunk: UploadFile = File(...),
    chunk_index: int = Form(...),
    is_final: bool = Form(False)
) -> VideoChunkUploadResponse:
    """
    Upload video chunk during interview recording.
    
    Stores chunks temporarily and concatenates on final chunk.
    Uploads final video to Supabase Storage and updates interview metadata.
    
    Args:
        interview_id: UUID of the interview
        chunk: Video chunk file (WebM/MP4)
        chunk_index: Zero-indexed chunk number
        is_final: Whether this is the final chunk
        current_user: Authenticated candidate
        db: Database session
        
    Returns:
        Upload confirmation with timestamp
        
    Raises:
        404: Interview not found
        403: Not authorized
        507: Storage quota exceeded
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "video_chunk_upload_request",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id),
        chunk_index=chunk_index,
        is_final=is_final
    )

    interview_repo = InterviewRepository(db)

    # Get interview
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
            detail="Not authorized"
        )

    # Check video recording consent
    if not interview.video_recording_consent:
        logger.warning(
            "video_upload_without_consent",
            correlation_id=correlation_id,
            interview_id=str(interview_id)
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Video recording consent not granted"
        )

    try:
        # Read chunk data
        chunk_data = await chunk.read()

        # Create temporary storage directory
        import os
        import tempfile

        temp_dir = tempfile.gettempdir()
        interview_temp_dir = os.path.join(temp_dir, f"interview_{interview_id}")
        os.makedirs(interview_temp_dir, exist_ok=True)

        # Save chunk temporarily
        chunk_path = os.path.join(interview_temp_dir, f"chunk_{chunk_index}.webm")
        with open(chunk_path, "wb") as f:
            f.write(chunk_data)

        logger.info(
            "video_chunk_saved_temporarily",
            correlation_id=correlation_id,
            chunk_index=chunk_index,
            size_bytes=len(chunk_data)
        )

        # If final chunk, concatenate and upload
        if is_final:
            from app.models.video_recording import VideoRecording
            from app.utils.supabase_storage import SupabaseStorageClient

            # Concatenate all chunks
            final_video_data = bytearray()
            chunk_files = sorted([
                f for f in os.listdir(interview_temp_dir)
                if f.startswith("chunk_")
            ])

            for chunk_file in chunk_files:
                chunk_file_path = os.path.join(interview_temp_dir, chunk_file)
                with open(chunk_file_path, "rb") as f:
                    final_video_data.extend(f.read())

            logger.info(
                "video_chunks_concatenated",
                correlation_id=correlation_id,
                total_chunks=len(chunk_files),
                final_size_bytes=len(final_video_data)
            )

            # Upload to Supabase Storage
            storage_client = SupabaseStorageClient()

            # Assuming org_id is available (for MVP, use candidate_id as org_id)
            org_id = str(current_user.id)
            storage_path = await storage_client.upload_video(
                bytes(final_video_data),
                org_id,
                str(interview_id)
            )

            # Update interview with storage path
            interview.video_recording_url = storage_path
            interview.video_recording_status = "completed"

            # Create video recording metadata
            video_recording = VideoRecording(
                id=uuid.uuid4(),
                interview_id=interview_id,
                storage_path=storage_path,
                file_size_bytes=len(final_video_data),
                upload_started_at=datetime.utcnow(),
                upload_completed_at=datetime.utcnow(),
                recording_metadata={
                    "total_chunks": len(chunk_files),
                    "upload_correlation_id": correlation_id
                }
            )

            db.add(video_recording)
            await db.commit()

            # Clean up temporary files
            import shutil
            shutil.rmtree(interview_temp_dir, ignore_errors=True)

            logger.info(
                "video_upload_completed",
                correlation_id=correlation_id,
                interview_id=str(interview_id),
                storage_path=storage_path,
                file_size_mb=round(len(final_video_data) / (1024 * 1024), 2)
            )

        return VideoChunkUploadResponse(
            success=True,
            chunk_index=chunk_index,
            uploaded_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error(
            "video_chunk_upload_failed",
            correlation_id=correlation_id,
            interview_id=str(interview_id),
            chunk_index=chunk_index,
            error=str(e)
        )

        # Check for storage quota errors
        if "quota" in str(e).lower() or "storage" in str(e).lower():
            raise HTTPException(
                status_code=507,
                detail="Storage quota exceeded. Please contact support."
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video upload failed: {str(e)}"
        )


@router.post("/{interview_id}/consent", response_model=VideoConsentResponse)
async def submit_video_consent(
    interview_id: uuid.UUID,
    request: VideoConsentRequest,
    current_user: Annotated[Candidate, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> VideoConsentResponse:
    """
    Record candidate's video recording consent (GDPR compliance).
    
    Args:
        interview_id: UUID of the interview
        request: Consent decision
        current_user: Authenticated candidate
        db: Database session
        
    Returns:
        Consent confirmation with video recording status
        
    Raises:
        404: Interview not found
        403: Not authorized
    """
    correlation_id = str(uuid.uuid4())

    logger.info(
        "video_consent_submission",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        candidate_id=str(current_user.id),
        consent=request.video_recording_consent
    )

    interview_repo = InterviewRepository(db)

    # Get interview
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
            detail="Not authorized"
        )

    # Update consent and status
    interview.video_recording_consent = request.video_recording_consent
    interview.video_recording_status = "recording" if request.video_recording_consent else "not_recorded"

    await db.commit()

    logger.info(
        "video_consent_recorded",
        correlation_id=correlation_id,
        interview_id=str(interview_id),
        consent=request.video_recording_consent,
        status=interview.video_recording_status
    )

    return VideoConsentResponse(
        success=True,
        video_recording_consent=request.video_recording_consent,
        video_recording_status=interview.video_recording_status
    )
