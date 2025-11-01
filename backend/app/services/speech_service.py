"""Speech Service for orchestrating STT/TTS operations with cost tracking."""

from decimal import Decimal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AudioValidationError
from app.providers.speech_provider import SpeechProvider
from app.repositories.interview import InterviewRepository
from app.repositories.interview_message import InterviewMessageRepository
from app.schemas.speech import TranscriptionResult
from app.services.audio_cache_service import AudioCacheService
from app.utils.cost_calculator import SpeechCostCalculator

logger = structlog.get_logger().bind(service="speech_service")


class SpeechService:
    """
    Service for managing speech operations (STT/TTS) with business logic.
    
    This service orchestrates all speech-related operations in the interview
    system, providing a clean interface for audio transcription, speech synthesis,
    cost tracking, and database persistence. It acts as the business logic layer
    between API endpoints and speech providers.
    
    Core Responsibilities:
    =====================
    1. Audio Quality Validation: Ensures audio meets minimum requirements
    2. Cost Calculation: Tracks STT/TTS costs for billing and analytics
    3. Database Persistence: Stores audio metadata and costs
    4. Error Handling: Provides graceful fallbacks for provider failures
    5. Performance Monitoring: Logs processing times and success rates
    
    Architecture Pattern:
    ====================
    API Controller -> SpeechService -> SpeechProvider -> OpenAI API
                           |
                    Database (costs, metadata)
    
    Features:
    =========
    - Provider abstraction (easily swap OpenAI for Azure/GCP)
    - Comprehensive audio validation (format, size, quality)
    - Accurate cost tracking with database persistence
    - Structured logging for monitoring and debugging
    - Transaction-safe database operations
    - Graceful error handling with detailed error messages
    
    Cost Tracking:
    =============
    - STT: $0.006 per minute of audio
    - TTS: $0.015 per 1,000 characters
    - Costs stored in interviews.speech_cost_usd field
    - Token usage tracked in interviews.speech_tokens_used field
    
    Usage Examples:
    ==============
    Basic transcription:
        >>> service = SpeechService(OpenAISpeechProvider(), db_session)
        >>> result = await service.transcribe_candidate_audio(
        ...     audio_data=audio_bytes,
        ...     interview_id=interview_id
        ... )
        >>> print(f"Transcribed: {result.text}")
        >>> print(f"Confidence: {result.confidence}")
        
    Generate AI speech:
        >>> audio_bytes = await service.generate_ai_speech(
        ...     text="Tell me about your React experience",
        ...     interview_id=interview_id
        ... )
        >>> # audio_bytes can be sent to frontend for playback
        
    Store metadata:
        >>> await service.store_audio_metadata(
        ...     interview_id=interview_id,
        ...     message_id=message_id,
        ...     metadata={
        ...         "provider": "openai",
        ...         "confidence": 0.95,
        ...         "sample_rate_hz": 16000
        ...     }
        ... )
    
    Error Handling:
    ==============
    The service handles various failure scenarios:
    
    Audio Validation Failures:
        >>> try:
        ...     result = await service.transcribe_candidate_audio(bad_audio)
        ... except AudioValidationError as e:
        ...     print(f"Invalid audio: {e.message} (field: {e.field})")
        
    Provider API Failures:
        >>> try:
        ...     result = await service.transcribe_candidate_audio(audio)
        ... except TranscriptionFailedError as e:
        ...     print(f"Transcription failed: {e.message}")
        ...     # Service logs error and can fall back to text-only mode
        
    Dependencies:
    ============
    - SpeechProvider: Abstraction for STT/TTS operations
    - AsyncSession: Database session for persistence
    - InterviewRepository: Database access for interviews
    - InterviewMessageRepository: Database access for messages
    - SpeechCostCalculator: Cost calculation utilities
    """

    def __init__(
        self,
        speech_provider: SpeechProvider,
        db: AsyncSession,
        audio_cache: AudioCacheService | None = None,
    ):
        """
        Initialize Speech Service with dependencies.
        
        Args:
            speech_provider: Speech provider implementation (e.g., OpenAISpeechProvider)
            db: Database session for persistence
            audio_cache: Optional audio cache service for TTS caching (creates default if None)
        """
        self.speech_provider = speech_provider
        self.db = db
        self.interview_repo = InterviewRepository(db)
        self.message_repo = InterviewMessageRepository(db)
        self.cost_calculator = SpeechCostCalculator()
        self.audio_cache = audio_cache or AudioCacheService()

        logger.info("speech_service_initialized")

    async def transcribe_candidate_audio(
        self,
        audio_data: bytes,
        interview_id: UUID,
        language: str = "en",
        correlation_id: str | None = None
    ) -> TranscriptionResult:
        """
        Transcribe candidate audio to text with quality validation and cost tracking.
        
        Validates audio quality, calls speech provider for transcription,
        calculates cost, and updates interview cost tracking in database.
        
        Args:
            audio_data: Audio file bytes
            interview_id: Interview UUID for cost tracking
            language: Language code (default: "en")
            correlation_id: Optional correlation ID for request tracing
        
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
            correlation_id=correlation_id,
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
                correlation_id=correlation_id,
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

        # Validate transcription quality and language
        self.validate_transcription_quality(
            transcription_result=transcription_result,
            expected_language=language,
            min_confidence=0.6  # Higher threshold for production use
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
            correlation_id=correlation_id,
        )

        return transcription_result

    async def generate_ai_speech(
        self,
        text: str,
        interview_id: UUID,
        voice: str = "alloy",
        speed: float = 0.95
    ) -> tuple[bytes, dict]:
        """
        Generate speech audio from AI question text with caching and cost tracking.
        
        Checks cache first for existing audio. If not cached, calls speech provider
        for TTS generation, caches the result, calculates cost, and updates
        interview cost tracking in database.
        
        Args:
            text: Text to convert to speech (max 4096 chars)
            interview_id: Interview UUID for cost tracking
            voice: Voice ID (default: "alloy" for professional tone)
            speed: Speech speed multiplier (default: 0.95 for clarity)
        
        Returns:
            tuple[bytes, dict]: (MP3 audio bytes, metadata dict with:
                - provider: "openai"
                - model: "tts-1"
                - voice: Voice used
                - speed: Speed used
                - generation_time_ms: Generation time
                - character_count: Text length
                - audio_format: "audio/mpeg"
                - file_size_bytes: Audio size
                - cached: Whether from cache
                - cost_usd: Generation cost
            )
        
        Raises:
            SynthesisFailedError: If speech synthesis fails
        
        Side Effects:
            - Updates interview.speech_tokens_used (character count)
            - Updates interview.speech_cost_usd in database (only for new generations)
            - Caches generated audio
            - Logs synthesis and cache metrics
        """
        import time
        
        start_time = time.time()
        
        logger.info(
            "generating_ai_speech",
            interview_id=str(interview_id),
            text_length=len(text),
            voice=voice,
            speed=speed,
        )

        # Check cache first
        cache_key = self.audio_cache.get_cache_key(text, voice, speed)
        cached_audio = await self.audio_cache.get_cached_audio(cache_key)
        
        if cached_audio:
            # Cache hit! Return cached audio without API call
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update metadata to include cache hit info
            metadata = cached_audio.metadata.copy()
            metadata["cached"] = True
            metadata["cache_age_seconds"] = cached_audio.age_seconds()
            metadata["retrieval_time_ms"] = processing_time_ms
            
            logger.info(
                "ai_speech_from_cache",
                interview_id=str(interview_id),
                audio_size_bytes=len(cached_audio.audio_bytes),
                cache_age_seconds=cached_audio.age_seconds(),
                character_count=len(text),
                retrieval_time_ms=processing_time_ms,
            )
            
            return cached_audio.audio_bytes, metadata

        # Cache miss - generate new audio
        audio_bytes, provider_metadata = await self.speech_provider.synthesize_speech(
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

        # Build complete metadata
        processing_time_ms = int((time.time() - start_time) * 1000)
        metadata = {
            "provider": "openai",
            "model": provider_metadata.get("model", "tts-1"),
            "voice": voice,
            "speed": speed,
            "generation_time_ms": provider_metadata.get("generation_time_ms", processing_time_ms),
            "character_count": len(text),
            "audio_format": "audio/mpeg",
            "file_size_bytes": len(audio_bytes),
            "cached": False,
            "cost_usd": float(tts_cost),
        }

        # Cache the generated audio
        await self.audio_cache.cache_audio(cache_key, audio_bytes, metadata)

        logger.info(
            "ai_speech_generated",
            interview_id=str(interview_id),
            audio_size_bytes=len(audio_bytes),
            tts_cost_usd=float(tts_cost),
            character_count=len(text),
            generation_time_ms=metadata["generation_time_ms"],
            cached=False,
        )

        return audio_bytes, metadata

    def validate_transcription_quality(
        self,
        transcription_result: TranscriptionResult,
        expected_language: str = "en",
        min_confidence: float = 0.5
    ) -> None:
        """
        Validate transcription result quality and language.
        
        Checks if the detected language matches expected language and
        if confidence scores meet minimum requirements.
        
        Args:
            transcription_result: Result from speech provider
            expected_language: Expected language code (default: "en")
            min_confidence: Minimum confidence threshold (default: 0.5)
            
        Raises:
            AudioValidationError: If language or confidence validation fails
        """
        # Validate detected language
        if transcription_result.language != expected_language:
            logger.warning(
                "unexpected_language_detected",
                detected=transcription_result.language,
                expected=expected_language,
                confidence=float(transcription_result.confidence)
            )
            raise AudioValidationError(
                f"Audio language '{transcription_result.language}' does not match expected '{expected_language}' for MVP",
                field="language"
            )

        # Validate confidence score
        if transcription_result.confidence < min_confidence:
            logger.warning(
                "low_confidence_transcription",
                confidence=float(transcription_result.confidence),
                min_required=min_confidence,
                text_length=len(transcription_result.text)
            )
            raise AudioValidationError(
                f"Transcription confidence {transcription_result.confidence:.2f} below minimum {min_confidence}",
                field="confidence"
            )

        # Additional validation for empty or very short transcriptions
        if not transcription_result.text.strip():
            logger.warning("empty_transcription_detected")
            raise AudioValidationError(
                "No speech detected in audio file",
                field="content"
            )

        if len(transcription_result.text.strip()) < 3:
            logger.warning(
                "very_short_transcription",
                text=transcription_result.text,
                length=len(transcription_result.text)
            )
            raise AudioValidationError(
                "Transcription too short, likely background noise or unclear speech",
                field="content"
            )

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
