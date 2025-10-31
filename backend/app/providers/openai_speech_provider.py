"""OpenAI provider implementation for speech services (Whisper STT + TTS)."""

import asyncio
import time
from io import BytesIO

import httpx
import structlog

from app.core.config import settings
from app.core.exceptions import (
    AudioValidationError,
    SpeechProviderError,
    SynthesisFailedError,
    TranscriptionFailedError,
)
from app.providers.speech_provider import SpeechProvider
from app.schemas.speech import TranscriptionResult

logger = structlog.get_logger()


class OpenAISpeechProvider(SpeechProvider):
    """
    OpenAI implementation for speech services using Whisper (STT) and TTS API.
    
    Features:
    - Speech-to-text using Whisper API with confidence scores
    - Text-to-speech using TTS API with neural voices
    - Automatic retry with exponential backoff for transient errors
    - Audio format validation (WAV, MP3, WebM, Opus)
    - Audio quality validation (sample rate, file size, duration)
    - Structured logging for monitoring
    - Cost tracking integration
    
    API Specifications:
    - Whisper: POST /v1/audio/transcriptions (25MB limit, $0.006/min)
    - TTS: POST /v1/audio/speech (4096 char limit, $0.015/1K chars)
    - Rate Limits: 50 requests/minute (tier 1)
    
    Usage:
        provider = OpenAISpeechProvider()
        
        # Transcribe audio
        result = await provider.transcribe_audio(audio_bytes, language="en")
        print(f"{result.text} (confidence: {result.confidence})")
        
        # Synthesize speech
        audio = await provider.synthesize_speech("Hello world", voice="alloy")
        with open("output.mp3", "wb") as f:
            f.write(audio)
    """
    
    # Supported audio MIME types for Whisper API
    SUPPORTED_FORMATS = [
        "audio/wav",
        "audio/mpeg",   # MP3
        "audio/webm",
        "audio/opus",
        "audio/m4a",
        "audio/mp4",
    ]
    
    # Valid TTS voice options
    VALID_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    # Max retry attempts for transient errors
    MAX_RETRIES = 3
    
    def __init__(self):
        """Initialize OpenAI speech provider with API credentials."""
        self.api_key = settings.openai_api_key.get_secret_value()
        self.base_url = "https://api.openai.com/v1"
        
        # Create HTTP client with configured timeouts
        self.stt_client = httpx.AsyncClient(
            timeout=settings.speech_stt_timeout_seconds,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            }
        )
        
        self.tts_client = httpx.AsyncClient(
            timeout=settings.speech_tts_timeout_seconds,
            headers={
                "Authorization": f"Bearer {self.api_key}",
            }
        )
        
        logger.info(
            "openai_speech_provider_initialized",
            stt_model=settings.openai_stt_model,
            tts_model=settings.openai_tts_model,
            tts_voice=settings.openai_tts_voice,
        )
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using OpenAI Whisper API.
        
        Makes a multipart/form-data POST request to Whisper API with retry logic
        for transient failures. Returns detailed transcription result including
        confidence scores and segment-level data.
        
        Args:
            audio_data: Audio file bytes in supported format
            language: Language code (default: "en")
        
        Returns:
            TranscriptionResult with text, confidence, duration, and metadata
        
        Raises:
            AudioValidationError: Invalid audio format or quality
            TranscriptionFailedError: API error or processing failure
        """
        start_time = time.time()
        
        logger.info(
            "transcribing_audio",
            audio_size_bytes=len(audio_data),
            language=language,
        )
        
        # Retry loop for transient errors
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                # Prepare multipart form data
                files = {
                    "file": ("audio.webm", BytesIO(audio_data), "audio/webm"),
                }
                data = {
                    "model": settings.openai_stt_model,
                    "language": language,
                    "response_format": "verbose_json",  # Get confidence scores
                }
                
                # Make API request
                response = await self.stt_client.post(
                    f"{self.base_url}/audio/transcriptions",
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                # Extract confidence from segments
                segments = result.get("segments", [])
                confidence = self._calculate_avg_confidence(segments)
                
                transcription_result = TranscriptionResult(
                    text=result["text"],
                    confidence=confidence,
                    duration_seconds=result.get("duration", 0.0),
                    language=result.get("language", language),
                    processing_time_ms=processing_time_ms,
                    segments=segments,
                )
                
                logger.info(
                    "transcription_complete",
                    text_length=len(transcription_result.text),
                    confidence=transcription_result.confidence,
                    duration_seconds=transcription_result.duration_seconds,
                    processing_time_ms=processing_time_ms,
                    attempt=attempt + 1,
                )
                
                return transcription_result
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                
                # Handle different HTTP errors
                if e.response.status_code == 400:
                    # Bad request - no retry
                    logger.error(
                        "transcription_validation_failed",
                        status_code=e.response.status_code,
                        response=e.response.text,
                    )
                    raise AudioValidationError(
                        f"Invalid audio format or parameters: {e.response.text}",
                        field="audio_data"
                    )
                
                elif e.response.status_code == 401:
                    # Auth error - no retry
                    logger.error("transcription_auth_failed")
                    raise TranscriptionFailedError(
                        "OpenAI API authentication failed. Check API key."
                    )
                
                elif e.response.status_code == 429:
                    # Rate limit - exponential backoff
                    retry_delay = 2 ** attempt
                    logger.warning(
                        "transcription_rate_limited",
                        attempt=attempt + 1,
                        retry_delay=retry_delay,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                
                elif e.response.status_code >= 500:
                    # Server error - retry with delay
                    retry_delay = 2
                    logger.warning(
                        "transcription_server_error",
                        status_code=e.response.status_code,
                        attempt=attempt + 1,
                        retry_delay=retry_delay,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                
                # For other errors or final retry, raise
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(
                        "transcription_failed_max_retries",
                        status_code=e.response.status_code,
                        attempts=self.MAX_RETRIES,
                    )
                    raise TranscriptionFailedError(
                        f"Transcription failed after {self.MAX_RETRIES} attempts: {e}"
                    )
            
            except httpx.TimeoutException:
                last_exception = TranscriptionFailedError("Transcription request timed out")
                logger.warning(
                    "transcription_timeout",
                    attempt=attempt + 1,
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(5)  # 5 second delay for timeout retry
                    continue
                else:
                    raise last_exception
            
            except Exception as e:
                logger.error(
                    "transcription_unexpected_error",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise TranscriptionFailedError(f"Unexpected transcription error: {e}")
        
        # Should not reach here, but handle it
        raise last_exception or TranscriptionFailedError("Transcription failed")
    
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech audio from text using OpenAI TTS API.
        
        Makes a JSON POST request to TTS API and returns MP3 audio bytes.
        Includes retry logic for transient failures.
        
        Args:
            text: Text to convert to speech (max 4096 chars)
            voice: Voice ID (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed multiplier (0.25-4.0)
        
        Returns:
            bytes: MP3 audio file bytes
        
        Raises:
            SynthesisFailedError: API error, text too long, or invalid parameters
        """
        start_time = time.time()
        
        # Validate inputs
        if not text or not text.strip():
            raise SynthesisFailedError("Text cannot be empty", text=text)
        
        if len(text) > 4096:
            raise SynthesisFailedError(
                f"Text exceeds OpenAI TTS limit of 4096 characters (got {len(text)})",
                text=text
            )
        
        if voice not in self.VALID_VOICES:
            raise SynthesisFailedError(
                f"Invalid voice '{voice}'. Must be one of: {', '.join(self.VALID_VOICES)}",
                text=text
            )
        
        if not (0.25 <= speed <= 4.0):
            raise SynthesisFailedError(
                f"Invalid speed {speed}. Must be between 0.25 and 4.0",
                text=text
            )
        
        logger.info(
            "synthesizing_speech",
            text_length=len(text),
            voice=voice,
            speed=speed,
        )
        
        # Retry loop for transient errors
        last_exception = None
        for attempt in range(self.MAX_RETRIES):
            try:
                # Make API request
                response = await self.tts_client.post(
                    f"{self.base_url}/audio/speech",
                    json={
                        "model": settings.openai_tts_model,
                        "input": text,
                        "voice": voice,
                        "speed": speed,
                    }
                )
                response.raise_for_status()
                
                # Get audio bytes
                audio_bytes = response.content
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                logger.info(
                    "synthesis_complete",
                    audio_size_bytes=len(audio_bytes),
                    processing_time_ms=processing_time_ms,
                    attempt=attempt + 1,
                )
                
                return audio_bytes
                
            except httpx.HTTPStatusError as e:
                last_exception = e
                
                # Handle different HTTP errors (same pattern as transcription)
                if e.response.status_code == 400:
                    logger.error(
                        "synthesis_validation_failed",
                        status_code=e.response.status_code,
                        response=e.response.text,
                    )
                    raise SynthesisFailedError(
                        f"Invalid TTS parameters: {e.response.text}",
                        text=text
                    )
                
                elif e.response.status_code == 401:
                    logger.error("synthesis_auth_failed")
                    raise SynthesisFailedError(
                        "OpenAI API authentication failed. Check API key.",
                        text=text
                    )
                
                elif e.response.status_code == 429:
                    retry_delay = 2 ** attempt
                    logger.warning(
                        "synthesis_rate_limited",
                        attempt=attempt + 1,
                        retry_delay=retry_delay,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                
                elif e.response.status_code >= 500:
                    retry_delay = 2
                    logger.warning(
                        "synthesis_server_error",
                        status_code=e.response.status_code,
                        attempt=attempt + 1,
                        retry_delay=retry_delay,
                    )
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(retry_delay)
                        continue
                
                if attempt == self.MAX_RETRIES - 1:
                    logger.error(
                        "synthesis_failed_max_retries",
                        status_code=e.response.status_code,
                        attempts=self.MAX_RETRIES,
                    )
                    raise SynthesisFailedError(
                        f"Synthesis failed after {self.MAX_RETRIES} attempts: {e}",
                        text=text
                    )
            
            except httpx.TimeoutException:
                last_exception = SynthesisFailedError("TTS request timed out", text=text)
                logger.warning(
                    "synthesis_timeout",
                    attempt=attempt + 1,
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(5)
                    continue
                else:
                    raise last_exception
            
            except Exception as e:
                logger.error(
                    "synthesis_unexpected_error",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise SynthesisFailedError(f"Unexpected synthesis error: {e}", text=text)
        
        raise last_exception or SynthesisFailedError("Synthesis failed", text=text)
    
    def get_supported_audio_formats(self) -> list[str]:
        """
        Get list of supported audio MIME types.
        
        Returns:
            List of MIME types supported by OpenAI Whisper
        """
        return self.SUPPORTED_FORMATS.copy()
    
    def validate_audio_quality(self, audio_metadata: dict) -> bool:
        """
        Validate audio quality meets OpenAI Whisper requirements.
        
        Checks:
        - Sample rate >= 16kHz (if provided)
        - File size < 25MB
        - Duration > 0.1 seconds
        - Format in supported list
        
        Args:
            audio_metadata: Dict with sample_rate_hz, file_size_bytes, 
                          duration_seconds, format
        
        Returns:
            True if audio quality is acceptable, False otherwise
        """
        try:
            # Check file size (25MB = 26,214,400 bytes)
            file_size = audio_metadata.get("file_size_bytes", 0)
            if file_size > settings.audio_max_file_size_mb * 1024 * 1024:
                logger.warning(
                    "audio_validation_failed",
                    reason="file_too_large",
                    file_size_mb=file_size / (1024 * 1024),
                    max_size_mb=settings.audio_max_file_size_mb,
                )
                return False
            
            # Check duration (if provided)
            duration = audio_metadata.get("duration_seconds", 1.0)
            if duration < settings.audio_min_duration_seconds:
                logger.warning(
                    "audio_validation_failed",
                    reason="duration_too_short",
                    duration_seconds=duration,
                    min_duration=settings.audio_min_duration_seconds,
                )
                return False
            
            # Check sample rate (if provided)
            sample_rate = audio_metadata.get("sample_rate_hz")
            if sample_rate and sample_rate < settings.audio_min_sample_rate_hz:
                logger.warning(
                    "audio_validation_failed",
                    reason="sample_rate_too_low",
                    sample_rate_hz=sample_rate,
                    min_sample_rate_hz=settings.audio_min_sample_rate_hz,
                )
                return False
            
            # Check format (if provided)
            audio_format = audio_metadata.get("format")
            if audio_format and audio_format not in self.SUPPORTED_FORMATS:
                logger.warning(
                    "audio_validation_failed",
                    reason="unsupported_format",
                    format=audio_format,
                    supported_formats=self.SUPPORTED_FORMATS,
                )
                return False
            
            logger.info(
                "audio_validation_passed",
                file_size_bytes=file_size,
                duration_seconds=duration,
                sample_rate_hz=sample_rate,
                format=audio_format,
            )
            return True
            
        except Exception as e:
            logger.error(
                "audio_validation_error",
                error=str(e),
                metadata=audio_metadata,
            )
            return False
    
    def _calculate_avg_confidence(self, segments: list[dict]) -> float:
        """
        Calculate average confidence score from Whisper segments.
        
        Args:
            segments: List of segment dicts with 'confidence' or 'avg_logprob'
        
        Returns:
            Average confidence score between 0.0 and 1.0
        """
        if not segments:
            return 0.85  # Default confidence when segments not available
        
        confidences = []
        for segment in segments:
            # Whisper may provide 'no_speech_prob' or 'avg_logprob'
            # Convert to 0-1 confidence score
            if "confidence" in segment:
                confidences.append(segment["confidence"])
            elif "avg_logprob" in segment:
                # Convert log probability to confidence (approximate)
                # avg_logprob ranges from -infinity to 0
                # Convert to 0-1 scale (this is an approximation)
                logprob = segment["avg_logprob"]
                confidence = min(1.0, max(0.0, (logprob + 1.0)))
                confidences.append(confidence)
        
        if confidences:
            return sum(confidences) / len(confidences)
        
        return 0.85  # Default if no confidence data available
    
    async def close(self):
        """Close HTTP clients and cleanup resources."""
        await self.stt_client.aclose()
        await self.tts_client.aclose()
        logger.info("openai_speech_provider_closed")
