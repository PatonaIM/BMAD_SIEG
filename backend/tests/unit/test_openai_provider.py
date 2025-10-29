"""Unit tests for OpenAI provider."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import Request, Response
from openai import APIError, APITimeoutError, AuthenticationError, RateLimitError

from app.core.exceptions import (
    ContextLengthExceededError,
    OpenAIProviderError,
    RateLimitExceededError,
)
from app.providers.openai_provider import OpenAIProvider


def create_mock_response(status_code: int = 200) -> Response:
    """Create a mock httpx Response for OpenAI exceptions."""
    request = Request("POST", "https://api.openai.com/v1/chat/completions")
    return Response(status_code=status_code, request=request)


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("app.providers.openai_provider.settings") as mock:
        mock.openai_api_key.get_secret_value.return_value = "sk-test-key"
        mock.openai_model = "gpt-4o-mini"
        mock.openai_max_tokens = 1000
        mock.openai_temperature = 0.7
        yield mock


@pytest.fixture
def provider(mock_settings):
    """Create OpenAIProvider instance for testing."""
    with patch("app.providers.openai_provider.ChatOpenAI") as mock_chat:
        # Create a mock LLM instance
        mock_llm = AsyncMock()
        mock_chat.return_value = mock_llm

        provider = OpenAIProvider()
        provider.llm = mock_llm  # Ensure the mock is set
        yield provider


@pytest.mark.asyncio
async def test_generate_completion_success(provider):
    """Test successful completion generation."""
    messages = [
        {"role": "system", "content": "You are an interviewer"},
        {"role": "user", "content": "Tell me about React"},
    ]

    # Mock the LLM response
    mock_response = Mock()
    mock_response.content = "React is a JavaScript library for building user interfaces."

    provider.llm.ainvoke.return_value = mock_response

    result = await provider.generate_completion(messages)

    assert result == "React is a JavaScript library for building user interfaces."
    provider.llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_generate_completion_rate_limit_retry(provider):
    """Test retry logic for rate limit errors."""
    messages = [{"role": "user", "content": "Test"}]

    # Mock rate limit error on first two calls, success on third
    mock_response = Mock()
    mock_response.content = "Success after retry"

    rate_limit_error = RateLimitError(
        "Rate limit exceeded",
        response=create_mock_response(429),
        body={"error": {"message": "Rate limit exceeded"}}
    )

    provider.llm.ainvoke.side_effect = [rate_limit_error, rate_limit_error, mock_response]

    result = await provider.generate_completion(messages)

    assert result == "Success after retry"
    assert provider.llm.ainvoke.call_count == 3


@pytest.mark.asyncio
async def test_generate_completion_rate_limit_exhausted(provider):
    """Test rate limit error after all retries exhausted."""
    messages = [{"role": "user", "content": "Test"}]

    # Mock rate limit error on all attempts
    rate_limit_error = RateLimitError(
        "Rate limit exceeded",
        response=create_mock_response(429),
        body={"error": {"message": "Rate limit exceeded"}}
    )

    provider.llm.ainvoke.side_effect = rate_limit_error

    with pytest.raises(RateLimitExceededError):
        await provider.generate_completion(messages)

    assert provider.llm.ainvoke.call_count == 3


@pytest.mark.asyncio
async def test_generate_completion_timeout_retry(provider):
    """Test retry logic for timeout errors."""
    messages = [{"role": "user", "content": "Test"}]

    # Mock timeout on first call, success on second
    mock_response = Mock()
    mock_response.content = "Success after timeout retry"

    timeout_error = APITimeoutError(request=Request("POST", "https://api.openai.com"))

    provider.llm.ainvoke.side_effect = [timeout_error, mock_response]

    result = await provider.generate_completion(messages)

    assert result == "Success after timeout retry"
    assert provider.llm.ainvoke.call_count == 2


@pytest.mark.asyncio
async def test_generate_completion_authentication_error(provider):
    """Test authentication error (no retry)."""
    messages = [{"role": "user", "content": "Test"}]

    auth_error = AuthenticationError(
        "Invalid API key",
        response=create_mock_response(401),
        body={"error": {"message": "Invalid API key"}}
    )

    provider.llm.ainvoke.side_effect = auth_error

    with pytest.raises(AuthenticationError):
        await provider.generate_completion(messages)

    # Should not retry authentication errors
    assert provider.llm.ainvoke.call_count == 1


@pytest.mark.asyncio
async def test_generate_completion_api_error_retry(provider):
    """Test retry logic for generic API errors."""
    messages = [{"role": "user", "content": "Test"}]

    # Mock API error on first call, success on second
    mock_response = Mock()
    mock_response.content = "Success after API error retry"

    api_error = APIError(
        "Server error",
        request=Request("POST", "https://api.openai.com"),
        body={"error": {"message": "Server error"}}
    )

    provider.llm.ainvoke.side_effect = [api_error, mock_response]

    result = await provider.generate_completion(messages)

    assert result == "Success after API error retry"
    assert provider.llm.ainvoke.call_count == 2


@pytest.mark.asyncio
async def test_generate_completion_context_length_error(provider):
    """Test context length error detection."""
    messages = [{"role": "user", "content": "Test"}]

    context_error = Exception("Context length exceeded for model")

    provider.llm.ainvoke.side_effect = context_error

    with pytest.raises(ContextLengthExceededError):
        await provider.generate_completion(messages)


@pytest.mark.asyncio
async def test_count_tokens(provider):
    """Test token counting."""
    text = "Hello, how are you doing today?"

    # Mock tiktoken encoding
    with patch("app.providers.openai_provider.tiktoken.encoding_for_model") as mock_encoding:
        mock_enc = Mock()
        mock_enc.encode.return_value = [1, 2, 3, 4, 5, 6, 7]  # 7 tokens
        mock_encoding.return_value = mock_enc

        count = await provider.count_tokens(text)

        assert count == 7
        mock_enc.encode.assert_called_once_with(text)


@pytest.mark.asyncio
async def test_count_tokens_error(provider):
    """Test token counting error handling."""
    with patch("app.providers.openai_provider.tiktoken.encoding_for_model") as mock_encoding:
        mock_encoding.side_effect = Exception("Encoding error")

        with pytest.raises(OpenAIProviderError):
            await provider.count_tokens("test text")


def test_convert_to_langchain_messages(provider):
    """Test message conversion to LangChain format."""
    messages = [
        {"role": "system", "content": "System prompt"},
        {"role": "user", "content": "User message"},
        {"role": "assistant", "content": "Assistant response"},
    ]

    langchain_messages = provider._convert_to_langchain_messages(messages)

    assert len(langchain_messages) == 3
    # Verify message types (check class names since we can't import LangChain classes here easily)
    assert "SystemMessage" in str(type(langchain_messages[0]))
    assert "HumanMessage" in str(type(langchain_messages[1]))
    assert "AIMessage" in str(type(langchain_messages[2]))


def test_convert_unknown_role(provider):
    """Test handling of unknown message roles."""
    messages = [
        {"role": "unknown", "content": "Unknown role message"},
    ]

    # Should default to HumanMessage for unknown roles
    langchain_messages = provider._convert_to_langchain_messages(messages)

    assert len(langchain_messages) == 1
    assert "HumanMessage" in str(type(langchain_messages[0]))
