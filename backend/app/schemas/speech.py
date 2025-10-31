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
