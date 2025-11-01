"""Pydantic schemas for speech services (STT/TTS)."""


from pydantic import BaseModel, Field


class TranscriptionResult(BaseModel):
    """
    Result of speech-to-text transcription.
    
    Contains the transcribed text along with metadata about the transcription
    quality, duration, and processing performance.
    """

    text: str = Field(..., description="Transcribed text from audio")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Transcription confidence score (0.0-1.0)")
    duration_seconds: float = Field(..., gt=0, description="Audio duration in seconds")
    language: str = Field(..., description="Detected or specified language code (e.g., 'en')")
    processing_time_ms: int = Field(..., ge=0, description="Time taken to process transcription in milliseconds")
    segments: list[dict] | None = Field(None, description="Detailed segment-level transcription data")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "text": "Tell me about your React experience",
                "confidence": 0.95,
                "duration_seconds": 5.2,
                "language": "en",
                "processing_time_ms": 1200,
                "segments": [
                    {
                        "text": "Tell me about your React experience",
                        "start": 0.0,
                        "end": 5.2,
                        "confidence": 0.95
                    }
                ]
            }
        }


class AudioMetadata(BaseModel):
    """
    Metadata about audio file for validation and storage.
    
    Used to validate audio quality before processing and to store
    processing details in the database.
    """

    provider: str = Field(..., description="Speech provider used (e.g., 'openai')")
    model: str = Field(..., description="Model used for processing (e.g., 'whisper-1')")
    format: str = Field(..., description="Audio MIME type (e.g., 'audio/webm')")
    file_size_bytes: int = Field(..., gt=0, description="Audio file size in bytes")
    sample_rate_hz: int | None = Field(None, gt=0, description="Audio sample rate in Hz")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Overall confidence score")
    processing_time_ms: int | None = Field(None, ge=0, description="Processing time in milliseconds")
    language: str | None = Field(None, description="Audio language code")
    segments: list[dict] | None = Field(None, description="Segment-level details")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "model": "whisper-1",
                "format": "audio/webm",
                "file_size_bytes": 125000,
                "sample_rate_hz": 16000,
                "confidence": 0.95,
                "processing_time_ms": 1200,
                "language": "en",
                "segments": [
                    {
                        "text": "segment text",
                        "start": 0.0,
                        "end": 2.5,
                        "confidence": 0.93
                    }
                ]
            }
        }


class AudioProcessingRequest(BaseModel):
    """
    Request model for audio processing endpoint.
    
    Used for POST /api/v1/interviews/{interview_id}/audio
    Note: The actual audio file is uploaded as multipart/form-data,
    this model handles optional metadata parameters.
    """

    message_sequence: int | None = Field(
        None,
        ge=1,
        description="Optional sequence number for message ordering"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message_sequence": 5
            }
        }


class AudioProcessingResponse(BaseModel):
    """
    Response model for successful audio processing.
    
    Contains transcription result, confidence metrics, and processing metadata.
    Returned from POST /api/v1/interviews/{interview_id}/audio
    """

    transcription: str = Field(..., description="Transcribed text from audio")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall transcription confidence")
    processing_time_ms: int = Field(..., ge=0, description="Total processing time in milliseconds")
    audio_metadata: AudioMetadata = Field(..., description="Detailed audio processing metadata")
    next_question_ready: bool = Field(..., description="Whether next AI question is ready")
    message_id: str = Field(..., description="UUID of created interview message")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "transcription": "Tell me about your React experience and how you handle state management",
                "confidence": 0.95,
                "processing_time_ms": 1240,
                "audio_metadata": {
                    "provider": "openai",
                    "model": "whisper-1",
                    "format": "audio/webm",
                    "file_size_bytes": 125000,
                    "sample_rate_hz": 16000,
                    "confidence": 0.95,
                    "processing_time_ms": 1200,
                    "language": "en"
                },
                "next_question_ready": True,
                "message_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class AudioValidationError(BaseModel):
    """
    Error response for audio validation failures.
    """

    error: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(..., description="Additional error details")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "AUDIO_VALIDATION_FAILED",
                "message": "Audio file exceeds maximum size limit",
                "details": {
                    "field": "file_size",
                    "limit_mb": 25,
                    "actual_mb": 30
                }
            }
        }


class TranscriptionError(BaseModel):
    """
    Error response for transcription processing failures.
    """

    error: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(..., description="Additional error details")
    retry_after_seconds: int | None = Field(None, description="Retry delay for rate limiting")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "TRANSCRIPTION_FAILED",
                "message": "OpenAI API temporarily unavailable",
                "details": {
                    "provider": "openai",
                    "status_code": 503,
                    "correlation_id": "req_123abc"
                },
                "retry_after_seconds": 30
            }
        }


class TTSGenerationRequest(BaseModel):
    """
    Request model for text-to-speech generation.
    
    Used for POST /api/v1/interviews/{interview_id}/messages/{message_id}/generate-audio
    to trigger on-demand TTS generation with custom parameters.
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Text to convert to speech (max 4096 characters per OpenAI limit)"
    )
    voice: str = Field(
        default="alloy",
        description="Voice to use for TTS (alloy, echo, fable, onyx, nova, shimmer)"
    )
    speed: float = Field(
        default=0.95,
        ge=0.25,
        le=4.0,
        description="Speech rate (0.25 to 4.0, default: 0.95 for clarity)"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "text": "Tell me about your experience with React and state management.",
                "voice": "alloy",
                "speed": 0.95
            }
        }


class TTSGenerationResponse(BaseModel):
    """
    Response model for successful TTS generation.
    
    Contains audio URL, generation metadata, and performance metrics.
    Returned from POST /api/v1/interviews/{interview_id}/messages/{message_id}/generate-audio
    """

    audio_url: str = Field(
        ...,
        description="URL to access generated audio file (GET endpoint)"
    )
    generation_time_ms: int = Field(
        ...,
        ge=0,
        description="Time taken to generate audio in milliseconds"
    )
    audio_metadata: dict = Field(
        ...,
        description="Detailed TTS metadata (provider, model, voice, speed, cost, etc.)"
    )
    cached: bool = Field(
        ...,
        description="Whether audio was served from cache (true) or newly generated (false)"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "audio_url": "/api/v1/interviews/550e8400-e29b-41d4-a716-446655440000/audio/123e4567-e89b-12d3-a456-426614174000",
                "generation_time_ms": 1240,
                "audio_metadata": {
                    "provider": "openai",
                    "model": "tts-1",
                    "voice": "alloy",
                    "speed": 0.95,
                    "character_count": 125,
                    "audio_format": "audio/mpeg",
                    "file_size_bytes": 45000,
                    "cached": False,
                    "cost_usd": 0.001875
                },
                "cached": False
            }
        }


class TTSError(BaseModel):
    """
    Error response for TTS generation failures.
    """

    error: str = Field(..., description="Error code identifier")
    message: str = Field(..., description="Human-readable error message")
    details: dict = Field(..., description="Additional error details")
    retry_after_seconds: int | None = Field(None, description="Retry delay for rate limiting")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "TTS_GENERATION_FAILED",
                "message": "Failed to generate audio after 3 retry attempts",
                "details": {
                    "message_id": "550e8400-e29b-41d4-a716-446655440000",
                    "text_length": 125,
                    "retry_attempts": 3
                },
                "retry_after_seconds": None
            }
        }
