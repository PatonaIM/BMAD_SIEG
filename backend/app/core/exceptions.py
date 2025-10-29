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
