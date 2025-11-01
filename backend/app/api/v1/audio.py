"""Audio processing API endpoints for interview speech-to-text."""

import asyncio
import time
from collections.abc import Callable
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import AudioValidationError, TranscriptionFailedError
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.providers.openai_provider import OpenAIProvider
from app.providers.openai_speech_provider import OpenAISpeechProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.repositories.interview_session import InterviewSessionRepository
from app.schemas.speech import AudioProcessingResponse, TranscriptionResult
from app.services.interview_engine import InterviewEngine
from app.services.speech_service import SpeechService

logger = structlog.get_logger().bind(module="audio_api")

router = APIRouter(prefix="/interviews", tags=["audio"])


# Audio file validation constants
MAX_FILE_SIZE_MB = 25
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "audio/webm",
    "audio/mp3",
    "audio/mpeg",
    "audio/wav",
    "audio/ogg",
    "audio/opus"
}


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    correlation_id: str = "unknown"
) -> any:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        correlation_id: ID for tracking in logs
        
    Returns:
        Result from successful function call
        
    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                logger.error(
                    "retry_attempts_exhausted",
                    correlation_id=correlation_id,
                    attempt=attempt + 1,
                    max_retries=max_retries,
                    error=str(e),
                    error_type=type(e).__name__
                )
                break

            # Calculate delay with exponential backoff
            delay = min(base_delay * (backoff_factor ** attempt), max_delay)

            logger.warning(
                "retry_attempt_failed",
                correlation_id=correlation_id,
                attempt=attempt + 1,
                max_retries=max_retries,
                error=str(e),
                error_type=type(e).__name__,
                retry_delay_seconds=delay
            )

            await asyncio.sleep(delay)

    # Re-raise the last exception if all retries failed
    raise last_exception


async def transcribe_with_retry(
    speech_service: SpeechService,
    audio_data: bytes,
    interview_id: UUID,
    language: str,
    correlation_id: str,
    max_retries: int = 3,
    base_delay: float = 1.0
    ) -> TranscriptionResult:
    """
    Transcribe audio with exponential backoff retry logic.
    
    Args:
        speech_service: Speech service instance
        audio_data: Audio file bytes
        interview_id: Interview UUID
        language: Language code
        correlation_id: Request correlation ID
        max_retries: Maximum retry attempts (default: 3)
        base_delay: Base delay in seconds (default: 1.0)
        
    Returns:
        TranscriptionResult: Result from speech service
        
    Raises:
        TranscriptionFailedError: If all retries fail
        HTTPException: For rate limiting or other specific errors
    """
    for attempt in range(max_retries + 1):
        try:
            return await speech_service.transcribe_candidate_audio(
                audio_data=audio_data,
                interview_id=interview_id,
                language=language,
                correlation_id=correlation_id
            )
        except TranscriptionFailedError as e:
            if attempt == max_retries:
                raise

            # Check if it's a rate limit error
            if "rate_limit" in str(e).lower() or "429" in str(e):
                delay = base_delay * (2 ** attempt) + 30  # Extra delay for rate limits
                logger.warning(
                    "rate_limit_detected_retrying",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id,
                    attempt=attempt + 1,
                    delay_seconds=delay
                )

                # Return rate limit error immediately
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "RATE_LIMIT_EXCEEDED",
                        "message": "OpenAI API rate limit exceeded",
                        "details": {
                            "correlation_id": correlation_id,
                            "retry_after_seconds": int(delay)
                        },
                        "retry_after_seconds": int(delay)
                    }
                )

            delay = base_delay * (2 ** attempt)
            logger.warning(
                "transcription_failed_retrying",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                attempt=attempt + 1,
                error=str(e),
                delay_seconds=delay
            )

            await asyncio.sleep(delay)

        except AudioValidationError:
            # Don't retry validation errors
            raise

        except Exception as e:
            if attempt == max_retries:
                logger.error(
                    "transcription_retry_exhausted",
                    interview_id=str(interview_id),
                    correlation_id=correlation_id,
                    final_error=str(e)
                )
                raise TranscriptionFailedError(f"Transcription failed after {max_retries} retries: {str(e)}")

            delay = base_delay * (2 ** attempt)
            logger.warning(
                "transcription_error_retrying",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                attempt=attempt + 1,
                error=str(e),
                error_type=type(e).__name__,
                delay_seconds=delay
            )

            await asyncio.sleep(delay)


async def get_speech_service(db: AsyncSession = Depends(get_db)) -> SpeechService:
    """Dependency to create SpeechService instance."""
    speech_provider = OpenAISpeechProvider()
    return SpeechService(speech_provider=speech_provider, db=db)


async def get_interview_engine(db: AsyncSession = Depends(get_db)) -> InterviewEngine:
    """Dependency to create InterviewEngine instance."""
    from app.providers.openai_provider import OpenAIProvider

    ai_provider = OpenAIProvider()
    session_repo = InterviewSessionRepository(db)
    message_repo = InterviewMessageRepository(db)
    interview_repo = InterviewRepository(db)

    return InterviewEngine(
        ai_provider=ai_provider,
        session_repo=session_repo,
        message_repo=message_repo,
        interview_repo=interview_repo
    )


async def get_interview_engine(db: AsyncSession = Depends(get_db)) -> InterviewEngine:
    """Dependency to create InterviewEngine instance."""
    ai_provider = OpenAIProvider()
    session_repo = InterviewSessionRepository(db)
    message_repo = InterviewMessageRepository(db)
    interview_repo = InterviewRepository(db)
    return InterviewEngine(
        ai_provider=ai_provider,
        session_repo=session_repo,
        message_repo=message_repo,
        interview_repo=interview_repo
    )


async def validate_audio_file(audio_file: UploadFile) -> None:
    """
    Validate audio file before processing.
    
    Args:
        audio_file: Uploaded audio file
        
    Raises:
        HTTPException: If validation fails
    """
    # Check file size
    if audio_file.size and audio_file.size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "AUDIO_FILE_TOO_LARGE",
                "message": f"Audio file exceeds maximum size limit of {MAX_FILE_SIZE_MB}MB",
                "details": {
                    "field": "audio_file",
                    "limit_mb": MAX_FILE_SIZE_MB,
                    "actual_mb": round((audio_file.size or 0) / (1024 * 1024), 2)
                }
            }
        )

    # Check MIME type
    if audio_file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_AUDIO_FORMAT",
                "message": f"Audio format not supported. Allowed formats: {', '.join(ALLOWED_MIME_TYPES)}",
                "details": {
                    "field": "audio_file",
                    "provided_type": audio_file.content_type,
                    "allowed_types": list(ALLOWED_MIME_TYPES)
                }
            }
        )


async def validate_interview_access(
    interview_id: UUID,
    current_user: Candidate,
    db: AsyncSession
    ) -> Interview:
    """
    Validate that current user can access the interview.
    
    Args:
        interview_id: Interview UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Interview: The validated interview object
        
    Raises:
        HTTPException: If access validation fails
    """
    interview_repo = InterviewRepository(db)
    interview = await interview_repo.get_by_id(interview_id)

    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "INTERVIEW_NOT_FOUND",
                "message": "Interview not found",
                "details": {"interview_id": str(interview_id)}
            }
        )

    if interview.candidate_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "INTERVIEW_ACCESS_DENIED",
                "message": "You do not have access to this interview",
                "details": {"interview_id": str(interview_id)}
            }
        )

    if interview.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "INTERVIEW_COMPLETED",
                    "message": "Cannot upload audio to completed interview",
                    "details": {"interview_id": str(interview_id)}
                }
            )

    return interview
@router.post("/{interview_id}/audio", response_model=AudioProcessingResponse)
async def process_audio(
    interview_id: UUID,
    audio_file: UploadFile = File(..., description="Audio file to transcribe"),
    message_sequence: int = Form(None, description="Optional message sequence number"),
    current_user: Candidate = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    speech_service: SpeechService = Depends(get_speech_service),
    interview_engine: InterviewEngine = Depends(get_interview_engine)
) -> AudioProcessingResponse:
    """
    Process uploaded audio file and return transcription.
    
    Accepts audio file upload, validates it, transcribes using OpenAI Whisper,
    stores the result in the database, and integrates with the interview engine
    for conversation flow.
    
    Args:
        interview_id: Interview UUID
        audio_file: Uploaded audio file (WebM, MP3, WAV, Opus)
        message_sequence: Optional sequence number for message ordering
        current_user: Authenticated candidate
        db: Database session
        speech_service: Speech processing service
        
    Returns:
        AudioProcessingResponse with transcription and metadata
        
    Raises:
        HTTPException: For various error conditions (413, 400, 404, 403, 422, 500)
    """
    correlation_id = f"audio_{interview_id}_{int(time.time())}"
    start_time = time.time()
    validation_start = None
    transcription_start = None
    storage_start = None
    engine_start = None

    logger.info(
        "audio_processing_started",
        interview_id=str(interview_id),
        correlation_id=correlation_id,
        file_size_bytes=audio_file.size,
        content_type=audio_file.content_type,
        message_sequence=message_sequence
    )

    try:
        # Validate audio file
        validation_start = time.time()
        await validate_audio_file(audio_file)
        validation_time_ms = int((time.time() - validation_start) * 1000)

        # Validate interview access
        interview = await validate_interview_access(interview_id, current_user, db)

        # Read audio file
        audio_data = await audio_file.read()

        logger.info(
            "audio_validation_completed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            validation_time_ms=validation_time_ms,
            audio_size_bytes=len(audio_data)
        )

        # Process through speech service with retry logic
        transcription_start = time.time()
        transcription_result = await transcribe_with_retry(
            speech_service=speech_service,
            audio_data=audio_data,
            interview_id=interview_id,
            language="en",
            correlation_id=correlation_id
        )
        transcription_time_ms = int((time.time() - transcription_start) * 1000)

        logger.info(
            "transcription_completed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            transcription_time_ms=transcription_time_ms,
            text_length=len(transcription_result.text),
            confidence=float(transcription_result.confidence)
        )

        # Check if transcription exceeds SLA (3 seconds)
        if transcription_time_ms > 3000:
            logger.warning(
                "transcription_sla_violation",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                transcription_time_ms=transcription_time_ms,
                sla_threshold_ms=3000
            )

        # Database storage
        storage_start = time.time()

        # Calculate total processing time
        total_processing_time_ms = int((time.time() - start_time) * 1000)

        # Get interview session for storing message
        session_repo = InterviewSessionRepository(db)
        session = await session_repo.get_by_interview_id(interview_id)

        if not session:
            logger.error(
                "interview_session_not_found",
                interview_id=str(interview_id),
                correlation_id=correlation_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "INTERVIEW_SESSION_NOT_FOUND",
                    "message": "Interview session not found",
                    "details": {"interview_id": str(interview_id)}
                }
            )

        # Get next sequence number for message
        message_repo = InterviewMessageRepository(db)
        current_message_count = await message_repo.get_message_count_for_session(session.id)
        sequence_number = message_sequence if message_sequence else current_message_count + 1

        # Prepare audio metadata for storage
        audio_metadata = {
            "provider": "openai",
            "model": "whisper-1",
            "format": audio_file.content_type or "audio/webm",
            "file_size_bytes": len(audio_data),
            "sample_rate_hz": None,  # Not available from Whisper response
            "confidence": float(transcription_result.confidence),
            "processing_time_ms": transcription_result.processing_time_ms,
            "language": transcription_result.language,
            "duration_seconds": transcription_result.duration_seconds,
            "segments": transcription_result.segments,
            "correlation_id": correlation_id
        }

        # Store transcription in database
        message = await message_repo.create_message(
            interview_id=interview_id,
            session_id=session.id,
            message_type="candidate_response",
            content_text=transcription_result.text,
            sequence_number=sequence_number,
            content_audio_url=None,  # We're not storing audio files permanently for GDPR compliance
            audio_duration_seconds=int(transcription_result.duration_seconds),
            audio_metadata=audio_metadata,
            response_time_seconds=int(total_processing_time_ms / 1000)
        )

        # Commit the transaction
        await db.commit()
        storage_time_ms = int((time.time() - storage_start) * 1000)

        logger.info(
            "message_storage_completed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            storage_time_ms=storage_time_ms,
            message_id=str(message.id)
        )

        # Integrate with InterviewEngine to generate next AI question
        engine_start = time.time()
        try:
            interview_response = await interview_engine.process_candidate_response(
                interview_id=interview_id,
                session_id=session.id,
                response_text=transcription_result.text,
                role_type=interview.role_type
            )

            next_question_ready = True
            engine_time_ms = int((time.time() - engine_start) * 1000)

            logger.info(
                "interview_engine_response_generated",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                engine_time_ms=engine_time_ms,
                ai_question_length=len(interview_response.get("ai_response", "")),
                question_number=interview_response.get("question_number", 0),
                tokens_used=interview_response.get("tokens_used", 0)
            )

        except Exception as e:
            # Don't fail the audio processing if interview engine fails
            # The transcription is already saved
            logger.error(
                "interview_engine_integration_failed",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                error=str(e),
                error_type=type(e).__name__
            )
            next_question_ready = False

        # Calculate total processing time
        total_processing_time_ms = int((time.time() - start_time) * 1000)

        # Check if total processing exceeds SLA (5 seconds)
        if total_processing_time_ms > 5000:
            logger.warning(
                "total_processing_sla_violation",
                interview_id=str(interview_id),
                correlation_id=correlation_id,
                total_processing_time_ms=total_processing_time_ms,
                sla_threshold_ms=5000
            )

        logger.info(
            "audio_processing_completed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            total_processing_time_ms=total_processing_time_ms,
            validation_time_ms=validation_time_ms,
            transcription_time_ms=transcription_time_ms,
            storage_time_ms=storage_time_ms,
            engine_time_ms=engine_time_ms if 'engine_time_ms' in locals() else 0,
            transcription_length=len(transcription_result.text),
            confidence=float(transcription_result.confidence),
            success=True
        )

        # Build response
        return AudioProcessingResponse(
            transcription=transcription_result.text,
            confidence=transcription_result.confidence,
            processing_time_ms=total_processing_time_ms,
            audio_metadata=audio_metadata,
            next_question_ready=next_question_ready,
            message_id=str(message.id)
        )

    except AudioValidationError as e:
        logger.warning(
            "audio_validation_failed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "AUDIO_VALIDATION_FAILED",
                "message": str(e),
                "details": {"field": getattr(e, 'field', 'audio_data')}
            }
        )

    except TranscriptionFailedError as e:
        logger.error(
            "transcription_failed",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "TRANSCRIPTION_FAILED",
                "message": "Audio transcription failed",
                "details": {
                    "correlation_id": correlation_id,
                    "provider": "openai"
                }
            }
        )

    except Exception as e:
        logger.error(
            "audio_processing_error",
            interview_id=str(interview_id),
            correlation_id=correlation_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "AUDIO_PROCESSING_ERROR",
                "message": "Unexpected error during audio processing",
                "details": {"correlation_id": correlation_id}
            }
        )
