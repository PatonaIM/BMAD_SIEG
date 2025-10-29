"""OpenAI provider implementation using LangChain."""

import asyncio
import random

import structlog
import tiktoken
from langchain_openai import ChatOpenAI
from openai import (
    APIError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from app.core.config import settings
from app.core.exceptions import (
    ContextLengthExceededError,
    OpenAIProviderError,
    RateLimitExceededError,
)
from app.providers.base_ai_provider import AIProvider

logger = structlog.get_logger()


class OpenAIProvider(AIProvider):
    """
    OpenAI implementation of AIProvider using LangChain.

    Features:
    - GPT-4o-mini and GPT-4 support
    - Automatic retry with exponential backoff for transient errors
    - Token counting using tiktoken
    - Structured logging for monitoring
    - Context length error handling with truncation

    Usage:
        provider = OpenAIProvider()
        response = await provider.generate_completion(
            messages=[
                {"role": "system", "content": "You are an interviewer"},
                {"role": "user", "content": "Tell me about React"}
            ],
            max_tokens=1000,
            temperature=0.7
        )
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ):
        """
        Initialize OpenAI provider with configuration.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
            model: Model name (defaults to settings.openai_model)
            max_tokens: Max response tokens (defaults to settings.openai_max_tokens)
            temperature: Response randomness (defaults to settings.openai_temperature)
        """
        self.api_key = api_key or settings.openai_api_key.get_secret_value()
        self.model = model or settings.openai_model
        self.max_tokens = max_tokens or settings.openai_max_tokens
        self.temperature = temperature or settings.openai_temperature

        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=45,  # 45 second timeout for API calls
        )

        logger.info(
            "openai_provider_initialized",
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

    async def generate_completion(
        self,
        messages: list[dict[str, str]],
        **kwargs
    ) -> str:
        """
        Generate AI completion with retry logic and error handling.

        Implements exponential backoff for:
        - Rate limit errors (429)
        - Server errors (500)
        - Timeout errors

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Override parameters (max_tokens, temperature)

        Returns:
            str: Generated completion text

        Raises:
            OpenAIProviderError: For unrecoverable errors
            RateLimitExceededError: After all retry attempts exhausted
            ContextLengthExceededError: When context exceeds limits
            AuthenticationError: For invalid API keys
        """
        max_retries = 3
        attempt = 0

        # Override instance settings if provided
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        temperature = kwargs.get("temperature", self.temperature)

        while attempt < max_retries:
            try:
                # Convert messages to LangChain format
                langchain_messages = self._convert_to_langchain_messages(messages)

                # Generate completion
                response = await self.llm.ainvoke(
                    langchain_messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                completion_text = response.content

                # Log successful completion
                logger.info(
                    "openai_completion_generated",
                    model=self.model,
                    message_count=len(messages),
                    completion_length=len(completion_text),
                    attempt=attempt + 1,
                )

                return completion_text

            except RateLimitError as e:
                attempt += 1
                if attempt >= max_retries:
                    logger.error(
                        "openai_rate_limit_exceeded",
                        model=self.model,
                        max_retries=max_retries,
                        error=str(e),
                    )
                    raise RateLimitExceededError(
                        f"Rate limit exceeded after {max_retries} attempts"
                    ) from e

                # Exponential backoff: 1s, 2s, 4s + jitter
                delay = (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                logger.warning(
                    "openai_rate_limit_retry",
                    attempt=attempt,
                    delay=delay,
                    model=self.model,
                )
                await asyncio.sleep(delay)

            except APITimeoutError as e:
                attempt += 1
                if attempt >= max_retries:
                    logger.error(
                        "openai_timeout_exceeded",
                        model=self.model,
                        max_retries=max_retries,
                        error=str(e),
                    )
                    raise OpenAIProviderError(
                        f"API timeout after {max_retries} attempts"
                    ) from e

                logger.warning(
                    "openai_timeout_retry",
                    attempt=attempt,
                    delay=5,
                    model=self.model,
                )
                await asyncio.sleep(5)

            except AuthenticationError as e:
                # Do NOT retry authentication errors
                logger.critical(
                    "openai_authentication_failed",
                    model=self.model,
                    error=str(e),
                )
                # Re-raise the original error instead of creating a new one
                raise

            except APIError as e:
                attempt += 1
                if attempt >= max_retries:
                    logger.error(
                        "openai_api_error_exceeded",
                        model=self.model,
                        max_retries=max_retries,
                        error=str(e),
                    )
                    raise OpenAIProviderError(
                        f"OpenAI API error after {max_retries} attempts"
                    ) from e

                logger.warning(
                    "openai_api_error_retry",
                    attempt=attempt,
                    delay=5,
                    model=self.model,
                    error=str(e),
                )
                await asyncio.sleep(5)

            except Exception as e:
                # Handle context length errors
                error_str = str(e).lower()
                if "context" in error_str or "token" in error_str or "length" in error_str:
                    logger.error(
                        "openai_context_length_exceeded",
                        model=self.model,
                        message_count=len(messages),
                        error=str(e),
                    )
                    raise ContextLengthExceededError(
                        "Conversation context exceeds model limits. Truncation required."
                    ) from e

                # Unknown error
                logger.error(
                    "openai_unknown_error",
                    model=self.model,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise OpenAIProviderError(f"Unexpected error: {str(e)}") from e

        raise OpenAIProviderError("Max retries exceeded without success")

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.

        Token counting is essential for:
        - Cost tracking
        - Context window management
        - API usage monitoring

        Args:
            text: Text string to count tokens for

        Returns:
            int: Number of tokens

        Raises:
            OpenAIProviderError: If token counting fails
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            tokens = encoding.encode(text)
            token_count = len(tokens)

            logger.debug(
                "tokens_counted",
                model=self.model,
                token_count=token_count,
                text_length=len(text),
            )

            return token_count

        except Exception as e:
            logger.error(
                "token_counting_failed",
                model=self.model,
                error=str(e),
            )
            raise OpenAIProviderError(f"Token counting failed: {str(e)}") from e

    def _convert_to_langchain_messages(self, messages: list[dict[str, str]]) -> list:
        """
        Convert message dicts to LangChain message format.

        Args:
            messages: List of dicts with 'role' and 'content'

        Returns:
            List of LangChain message objects
        """
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        langchain_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                logger.warning(
                    "unknown_message_role",
                    role=role,
                    message=msg,
                )
                # Default to HumanMessage for unknown roles
                langchain_messages.append(HumanMessage(content=content))

        return langchain_messages
