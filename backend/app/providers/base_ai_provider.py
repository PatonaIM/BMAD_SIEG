"""Base abstract class for AI provider implementations."""

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Abstract base class for AI provider implementations.

    This abstraction enables easy switching between different AI providers
    (OpenAI, Azure, GCP, etc.) without changing business logic. It also
    simplifies testing by allowing mock implementations.

    Usage:
        provider = get_ai_provider()  # Returns OpenAIProvider or MockAIProvider
        response = await provider.generate_completion(messages)
        tokens = await provider.count_tokens(text)
    """

    @abstractmethod
    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate AI completion from a list of messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Example: [
                         {"role": "system", "content": "You are an interviewer"},
                         {"role": "user", "content": "Tell me about React"}
                     ]
            **kwargs: Additional provider-specific parameters like:
                     - max_tokens: Maximum tokens in response
                     - temperature: Randomness (0.0-2.0)

        Returns:
            str: The generated completion text.

        Raises:
            AIProviderError: For provider-specific errors
            RateLimitExceededError: When rate limits are hit
            ContextLengthExceededError: When context is too long
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text string.

        Token counting is provider-specific as different models use
        different tokenization strategies.

        Args:
            text: The text string to count tokens for.

        Returns:
            int: Number of tokens in the text.

        Raises:
            AIProviderError: If token counting fails
        """
        pass
