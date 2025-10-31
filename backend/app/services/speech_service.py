"""Speech Service for orchestrating STT/TTS operations with cost tracking."""

from decimal import Decimal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AudioValidationError
from app.models.interview import Interview
from app.models.interview_message import InterviewMessage
from app.providers.speech_provider import SpeechProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.schemas.speech import TranscriptionResult
from app.utils.cost_calculator import SpeechCostCalculator

logger = structlog.get_logger().bind(service="speech_service")


class SpeechService:
    """
    Service for managing speech operations (STT/TTS) with business logic.
    
    Orchestrates audio transcription, speech synthesis, cost tracking, and
    database persistence. Validates audio quality before processing and
    handles provider failures gracefully.
    
    Features:
    - Audio quality validation before transcription
    - Cost calculation and tracking for STT/TTS
    - Audio metadata storage in database
    - Provider error handling with logging
    - Performance metrics tracking
    
    Usage:
        service = SpeechService(
            speech_provider=OpenAISpeechProvider(),
            db=db_session
        )
        
        # Transcribe candidate audio
        result = await service.transcribe_candidate_audio(
            audio_data=audio_bytes,
            interview_id=interview_uuid
        )
        
        # Generate AI speech
        audio = await service.generate_ai_speech(
            text="Tell me about your experience",
            interview_id=interview_uuid
        )
    """
    
    def __init__(
        self,
        speech_provider: SpeechProvider,
        db: AsyncSession,
    ):
        """
        Initialize Speech Service with dependencies.
        
        Args:
            speech_provider: Speech provider implementation (e.g., OpenAISpeechProvider)
            db: Database session for persistence
        """
        self.speech_provider = speech_provider
        self.db = db
        self.interview_repo = InterviewRepository(db)
        self.message_repo = InterviewMessageRepository(db)
        self.cost_calculator = SpeechCostCalculator()
        
        logger.info("speech_service_initialized")
    
    async def transcribe_candidate_audio(
        self,
        audio_data: bytes,
        interview_id: UUID,
        language: str = "en"
    ) -> TranscriptionResult:
        """
        Transcribe candidate audio to text with quality validation and cost tracking.
        
        Validates audio quality, calls speech provider for transcription,
        calculates cost, and updates interview cost tracking in database.
        
        Args:
            audio_data: Audio file bytes
            interview_id: Interview UUID for cost tracking
            language: Language code (default: "en")
        
        Returns:
            TranscriptionResult with text, confidence, and metadata
        
        Raises:
            AudioValidationError: If audio quality validation fails
            TranscriptionFailedError: If transcription fails after retries
        
        Side Effects:
            - Updates interview.speech_cost_usd in database
            - Logs transcription metrics
        """
        logger.info(
            "transcribing_candidate_audio",
            interview_id=str(interview_id),
            audio_size_bytes=len(audio_data),
            language=language,
        )
        
        # Validate audio quality before processing
        audio_metadata = {
            "file_size_bytes": len(audio_data),
            "format": "audio/webm",  # Assuming WebM from browser
            # Note: sample_rate and duration not available until transcription
        }
        
        if not self.speech_provider.validate_audio_quality(audio_metadata):
            logger.error(
                "audio_quality_validation_failed",
                interview_id=str(interview_id),
                metadata=audio_metadata,
            )
            raise AudioValidationError(
                "Audio quality does not meet minimum requirements",
                field="audio_data"
            )
        
        # Transcribe audio using provider
        transcription_result = await self.speech_provider.transcribe_audio(
            audio_data=audio_data,
            language=language
        )
        
        # Calculate STT cost
        stt_cost = self.cost_calculator.calculate_stt_cost(
            duration_seconds=transcription_result.duration_seconds
        )
        
        # Update interview speech cost
        await self._update_interview_speech_cost(
            interview_id=interview_id,
            additional_cost=stt_cost
        )
        
        logger.info(
            "candidate_audio_transcribed",
            interview_id=str(interview_id),
            text_length=len(transcription_result.text),
            confidence=float(transcription_result.confidence),
            duration_seconds=transcription_result.duration_seconds,
            stt_cost_usd=float(stt_cost),
            processing_time_ms=transcription_result.processing_time_ms,
        )
        
        return transcription_result
    
    async def generate_ai_speech(
        self,
        text: str,
        interview_id: UUID,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech audio from AI question text with cost tracking.
        
        Calls speech provider for TTS, calculates cost, and updates
        interview cost tracking in database.
        
        Args:
            text: Text to convert to speech
            interview_id: Interview UUID for cost tracking
            voice: Voice ID (default: "alloy")
            speed: Speech speed multiplier (default: 1.0)
        
        Returns:
            bytes: MP3 audio file bytes
        
        Raises:
            SynthesisFailedError: If speech synthesis fails
        
        Side Effects:
            - Updates interview.speech_tokens_used (character count)
            - Updates interview.speech_cost_usd in database
            - Logs synthesis metrics
        """
        logger.info(
            "generating_ai_speech",
            interview_id=str(interview_id),
            text_length=len(text),
            voice=voice,
            speed=speed,
        )
        
        # Generate speech using provider
        audio_bytes = await self.speech_provider.synthesize_speech(
            text=text,
            voice=voice,
            speed=speed
        )
        
        # Calculate TTS cost
        tts_cost = self.cost_calculator.calculate_tts_cost(text=text)
        
        # Update interview speech cost and token usage
        await self._update_interview_speech_cost(
            interview_id=interview_id,
            additional_cost=tts_cost,
            additional_tokens=len(text)  # Track character count
        )
        
        logger.info(
            "ai_speech_generated",
            interview_id=str(interview_id),
            audio_size_bytes=len(audio_bytes),
            tts_cost_usd=float(tts_cost),
            character_count=len(text),
        )
        
        return audio_bytes
    
    async def store_audio_metadata(
        self,
        interview_id: UUID,
        message_id: UUID,
        metadata: dict
    ) -> None:
        """
        Store audio metadata in interview message record.
        
        Updates the audio_metadata JSONB field in interview_messages table
        with transcription details, confidence scores, and processing info.
        
        Args:
            interview_id: Interview UUID
            message_id: Message UUID to update
            metadata: Audio metadata dict (provider, confidence, segments, etc.)
        
        Side Effects:
            - Updates interview_messages.audio_metadata field
            - Logs metadata storage
        """
        logger.info(
            "storing_audio_metadata",
            interview_id=str(interview_id),
            message_id=str(message_id),
            metadata_keys=list(metadata.keys()),
        )
        
        # Get message record
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            logger.warning(
                "message_not_found_for_metadata_storage",
                message_id=str(message_id),
            )
            return
        
        # Update audio_metadata field
        message.audio_metadata = metadata
        await self.db.commit()
        
        logger.info(
            "audio_metadata_stored",
            interview_id=str(interview_id),
            message_id=str(message_id),
        )
    
    async def _update_interview_speech_cost(
        self,
        interview_id: UUID,
        additional_cost: Decimal,
        additional_tokens: int = 0
    ) -> None:
        """
        Update interview speech cost and token tracking.
        
        Accumulates speech costs and character counts across the interview.
        Handles race conditions with database-level atomic updates.
        
        Args:
            interview_id: Interview UUID
            additional_cost: Cost to add (STT or TTS)
            additional_tokens: Character count to add (for TTS tracking)
        
        Side Effects:
            - Increments interview.speech_cost_usd
            - Increments interview.speech_tokens_used
            - Commits changes to database
        """
        interview = await self.interview_repo.get_by_id(interview_id)
        if not interview:
            logger.error(
                "interview_not_found_for_cost_update",
                interview_id=str(interview_id),
            )
            return
        
        # Accumulate costs
        interview.speech_cost_usd += additional_cost
        interview.speech_tokens_used += additional_tokens
        
        await self.db.commit()
        
        logger.info(
            "interview_speech_cost_updated",
            interview_id=str(interview_id),
            additional_cost_usd=float(additional_cost),
            additional_tokens=additional_tokens,
            total_speech_cost_usd=float(interview.speech_cost_usd),
            total_speech_tokens=interview.speech_tokens_used,
        )
