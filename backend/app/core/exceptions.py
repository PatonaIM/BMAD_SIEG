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
