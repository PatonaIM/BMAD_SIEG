"""Custom exceptions for the application."""


class AIProviderError(Exception):
    """Base exception for AI provider errors."""
    pass


class OpenAIProviderError(AIProviderError):
    """Exception raised for OpenAI provider-specific errors."""
    pass


class RateLimitExceededError(AIProviderError):
    """
    Exception raised when API rate limits are exceeded.

    This typically triggers retry logic with exponential backoff.
    """
    pass


class ContextLengthExceededError(AIProviderError):
    """
    Exception raised when conversation context exceeds model limits.

    This typically triggers conversation history truncation.
    """
    pass


class InterviewNotFoundException(Exception):
    """
    Exception raised when interview_id is not found in database.
    
    HTTP Status: 404
    """
    pass


class InterviewCompletedException(Exception):
    """
    Exception raised when trying to send message to completed interview.
    
    HTTP Status: 400
    """
    pass


class InterviewAbandonedException(Exception):
    """
    Exception raised when trying to send message to abandoned interview.
    
    HTTP Status: 400
    """
    pass


class OpenAIRateLimitException(Exception):
    """
    Exception raised when OpenAI API rate limit is exceeded.
    
    HTTP Status: 429
    Includes retry-after header
    """
    def __init__(self, retry_after: int = 60):
        """
        Initialize with retry-after duration.
        
        Args:
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")


class ContextWindowExceededException(Exception):
    """
    Exception raised when conversation context exceeds model's token limit.
    
    HTTP Status: 400
    Suggests conversation truncation
    """
    pass


# Speech Provider Exceptions

class SpeechProviderError(Exception):
    """
    Base exception for speech provider errors.
    
    Raised for general speech service failures including STT and TTS operations.
    """

    def __init__(self, message: str, retry_after: int | None = None):
        """
        Initialize speech provider error.
        
        Args:
            message: Error description
            retry_after: Optional seconds to wait before retrying (for rate limits)
        """
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)


class AudioValidationError(SpeechProviderError):
    """
    Exception raised when audio validation fails.
    
    HTTP Status: 400
    Raised for invalid audio format, file size, sample rate, or duration issues.
    """

    def __init__(self, message: str, field: str):
        """
        Initialize audio validation error.
        
        Args:
            message: Error description
            field: Name of the validation field that failed (e.g., 'file_size', 'sample_rate')
        """
        self.field = field
        super().__init__(message)


class TranscriptionFailedError(SpeechProviderError):
    """
    Exception raised when speech-to-text transcription fails.
    
    HTTP Status: 500 (or appropriate error code based on underlying cause)
    Raised for API failures, processing errors, or authentication issues.
    """

    def __init__(self, message: str, audio_metadata: dict | None = None):
        """
        Initialize transcription failure error.
        
        Args:
            message: Error description
            audio_metadata: Optional audio file metadata for debugging
        """
        self.audio_metadata = audio_metadata or {}
        super().__init__(message)


class SynthesisFailedError(SpeechProviderError):
    """
    Exception raised when text-to-speech synthesis fails.
    
    HTTP Status: 500 (or appropriate error code based on underlying cause)
    Raised for API failures, text length exceeded, or invalid parameters.
    """

    def __init__(self, message: str, text: str | None = None):
        """
        Initialize synthesis failure error.
        
        Args:
            message: Error description
            text: Optional text that failed to synthesize (truncated for logging)
        """
        self.text = text[:100] if text else None  # Truncate for logging
        super().__init__(message)
