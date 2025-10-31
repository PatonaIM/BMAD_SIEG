"""Base abstract class for speech provider implementations (STT/TTS)."""

from abc import ABC, abstractmethod

from app.schemas.speech import TranscriptionResult


class SpeechProvider(ABC):
    """
    Abstract base class for speech service provider implementations.
    
    This abstraction enables easy switching between different speech providers
    (OpenAI Whisper/TTS, Azure Speech, GCP Speech, etc.) without changing
    business logic. It provides a unified interface for both speech-to-text (STT)
    and text-to-speech (TTS) operations.
    
    The provider handles:
    - Audio transcription (STT) with confidence scores
    - Speech synthesis (TTS) with voice selection
    - Audio format validation
    - Audio quality validation
    
    Usage:
        provider = OpenAISpeechProvider()
        
        # Transcribe audio to text
        result = await provider.transcribe_audio(audio_data, language="en")
        print(f"Transcription: {result.text} (confidence: {result.confidence})")
        
        # Generate speech from text
        audio_bytes = await provider.synthesize_speech(
            text="Tell me about your React experience",
            voice="alloy",
            speed=1.0
        )
    
    Future Implementations:
    - AzureSpeechProvider: Microsoft Azure Speech Services
    - GCPSpeechProvider: Google Cloud Speech-to-Text/Text-to-Speech
    - ElevenLabsSpeechProvider: ElevenLabs for high-quality TTS
    """

    @abstractmethod
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en"
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using speech-to-text API.
        
        Processes audio bytes and returns transcribed text with confidence scores
        and metadata. The method should handle various audio formats and provide
        detailed segment-level transcription data when available.
        
        Args:
            audio_data: Audio file bytes in supported format (WAV, MP3, WebM, Opus).
                       Must be < 25MB for OpenAI Whisper compatibility.
            language: Language code for transcription (e.g., "en", "es", "fr").
                     Defaults to "en" for English. Used to improve transcription
                     accuracy by hinting at the expected language.
        
        Returns:
            TranscriptionResult: Object containing:
                - text: Transcribed text string
                - confidence: Overall confidence score (0.0-1.0)
                - duration_seconds: Audio duration in seconds
                - language: Detected or specified language code
                - processing_time_ms: Time taken to process request
                - segments: Optional list of segment-level transcriptions
        
        Raises:
            AudioValidationError: If audio format is invalid, file size exceeds
                                 limits, or audio quality is insufficient.
            TranscriptionFailedError: If API call fails, authentication fails,
                                     or processing encounters errors.
            SpeechProviderError: For other provider-specific errors like
                                rate limits or timeouts.
        
        Example:
            >>> provider = OpenAISpeechProvider()
            >>> audio_data = open("recording.mp3", "rb").read()
            >>> result = await provider.transcribe_audio(audio_data, language="en")
            >>> print(result.text)
            "Tell me about your React experience"
            >>> print(result.confidence)
            0.95
        """
        pass

    @abstractmethod
    async def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech audio from text using text-to-speech API.
        
        Converts text input into natural-sounding speech audio with configurable
        voice selection and speed. Returns audio bytes in MP3 format for
        efficient transmission and playback.
        
        Args:
            text: Text to convert to speech. Maximum length depends on provider:
                 - OpenAI TTS: 4096 characters
                 - Azure: 10,000 characters
                 Must be non-empty and contain valid UTF-8 text.
            voice: Voice ID for synthesis. Provider-specific voice identifiers:
                  - OpenAI: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
                  - Azure: Various neural voices by language/gender
                  Defaults to "alloy" (neutral, professional tone).
            speed: Speech speed multiplier (0.25-4.0). Values:
                  - 0.5: Half speed (slower)
                  - 1.0: Normal speed (default)
                  - 1.5: 1.5x faster
                  - 2.0: Double speed
        
        Returns:
            bytes: Audio file bytes in MP3 format. Can be:
                  - Sent directly to frontend for playback
                  - Saved to file storage (S3, Supabase)
                  - Streamed in real-time (future enhancement)
        
        Raises:
            SynthesisFailedError: If API call fails, text exceeds length limits,
                                 or audio generation encounters errors.
            SpeechProviderError: For provider-specific errors like rate limits,
                                authentication failures, or invalid parameters.
        
        Example:
            >>> provider = OpenAISpeechProvider()
            >>> audio_bytes = await provider.synthesize_speech(
            ...     text="Tell me about your React experience",
            ...     voice="alloy",
            ...     speed=1.0
            ... )
            >>> with open("question.mp3", "wb") as f:
            ...     f.write(audio_bytes)
        """
        pass

    @abstractmethod
    def get_supported_audio_formats(self) -> list[str]:
        """
        Get list of supported audio MIME types for transcription.
        
        Returns the audio formats that this provider can process for speech-to-text.
        Used for validation before attempting transcription to provide early
        feedback on unsupported formats.
        
        Returns:
            list[str]: List of supported MIME types, such as:
                      - "audio/wav": Uncompressed WAV format
                      - "audio/mpeg": MP3 format
                      - "audio/webm": WebM format (common in browsers)
                      - "audio/opus": Opus codec
                      - "audio/m4a": M4A/MP4 audio
        
        Example:
            >>> provider = OpenAISpeechProvider()
            >>> formats = provider.get_supported_audio_formats()
            >>> print(formats)
            ['audio/wav', 'audio/mpeg', 'audio/webm', 'audio/opus']
            >>> mime_type = "audio/webm"
            >>> if mime_type in formats:
            ...     result = await provider.transcribe_audio(audio_data)
        """
        pass

    @abstractmethod
    def validate_audio_quality(self, audio_metadata: dict) -> bool:
        """
        Validate audio quality meets minimum requirements for transcription.
        
        Checks audio metadata to ensure the file meets provider requirements
        for sample rate, file size, duration, and format. This validation
        should be performed before attempting transcription to fail fast
        and provide clear error messages.
        
        Args:
            audio_metadata: Dictionary containing audio file properties:
                - sample_rate_hz: Sample rate in Hz (e.g., 16000, 44100)
                - file_size_bytes: File size in bytes
                - duration_seconds: Audio duration in seconds
                - format: Audio MIME type (e.g., "audio/webm")
        
        Returns:
            bool: True if audio quality is acceptable, False otherwise.
                 Providers should log specific validation failures for
                 debugging purposes.
        
        Validation Rules (OpenAI Whisper):
            - Sample rate: >= 16kHz (16000 Hz) for good transcription quality
            - File size: < 25MB (OpenAI API limit)
            - Duration: > 0.1 seconds (reject too-short audio)
            - Format: Must be in supported formats list
        
        Example:
            >>> provider = OpenAISpeechProvider()
            >>> metadata = {
            ...     "sample_rate_hz": 16000,
            ...     "file_size_bytes": 125000,
            ...     "duration_seconds": 5.2,
            ...     "format": "audio/webm"
            ... }
            >>> if provider.validate_audio_quality(metadata):
            ...     result = await provider.transcribe_audio(audio_data)
            ... else:
            ...     raise AudioValidationError("Audio quality insufficient")
        """
        pass
