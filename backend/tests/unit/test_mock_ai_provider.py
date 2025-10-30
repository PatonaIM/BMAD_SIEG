"""Unit tests for Mock AI Provider."""

from unittest.mock import Mock, patch

import pytest

from app.providers.mock_ai_provider import MockAIProvider, get_ai_provider
from app.providers.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_mock_provider_initialization():
    """Test MockAIProvider initializes with correct role type."""
    provider = MockAIProvider(role_type="react")

    assert provider.role_type == "react"
    assert provider.response_index == 0
    assert provider.call_count == 0


@pytest.mark.asyncio
async def test_generate_completion_returns_response():
    """Test mock completion generates a response."""
    provider = MockAIProvider(role_type="python")

    messages = [
        {"role": "system", "content": "You are an interviewer"},
        {"role": "user", "content": "Tell me about Python"}
    ]

    response = await provider.generate_completion(messages)

    assert isinstance(response, str)
    assert len(response) > 0
    assert provider.call_count == 1
    assert provider.response_index == 1


@pytest.mark.asyncio
async def test_generate_completion_cycles_through_responses():
    """Test mock provider cycles through response list."""
    provider = MockAIProvider(role_type="react")

    messages = [{"role": "user", "content": "Test"}]

    # Generate more responses than available in list
    responses = []
    for _ in range(10):
        response = await provider.generate_completion(messages)
        responses.append(response)

    # Verify it cycles (some responses should repeat)
    assert len(responses) == 10
    assert provider.call_count == 10
    # First response should match 8th response (cycling after 7 react responses)
    assert responses[0] == responses[7]


@pytest.mark.asyncio
async def test_generate_completion_different_role_types():
    """Test mock provider returns role-specific responses."""
    react_provider = MockAIProvider(role_type="react")
    python_provider = MockAIProvider(role_type="python")

    messages = [{"role": "user", "content": "Test"}]

    react_response = await react_provider.generate_completion(messages)
    python_response = await python_provider.generate_completion(messages)

    # Responses should be different for different roles
    assert react_response != python_response
    assert "React" in react_response
    assert "Python" in python_response


@pytest.mark.asyncio
async def test_generate_completion_uses_default_role():
    """Test mock provider falls back to default role for unknown type."""
    provider = MockAIProvider(role_type="unknown_role")

    messages = [{"role": "user", "content": "Test"}]
    response = await provider.generate_completion(messages)

    # Should fall back to javascript (default)
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_count_tokens_estimates_correctly():
    """Test token counting uses character estimation."""
    provider = MockAIProvider()

    text = "This is a test message"
    token_count = await provider.count_tokens(text)

    # Estimation: ~4 chars per token
    expected_tokens = len(text) // 4
    assert token_count == expected_tokens


@pytest.mark.asyncio
async def test_count_tokens_empty_string():
    """Test token counting with empty string."""
    provider = MockAIProvider()

    token_count = await provider.count_tokens("")

    assert token_count == 0


@pytest.mark.asyncio
async def test_factory_returns_mock_provider_when_enabled():
    """Test factory function returns MockAIProvider when USE_MOCK_AI=true."""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.use_mock_ai = True

        provider = get_ai_provider(role_type="react")

        assert isinstance(provider, MockAIProvider)
        assert provider.role_type == "react"


@pytest.mark.asyncio
async def test_factory_returns_openai_provider_when_disabled():
    """Test factory function returns OpenAIProvider when USE_MOCK_AI=false."""
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.use_mock_ai = False
        mock_settings.openai_api_key.get_secret_value.return_value = "sk-test"
        mock_settings.openai_model = "gpt-4o-mini"
        mock_settings.openai_max_tokens = 1000
        mock_settings.openai_temperature = 0.7

        with patch("app.providers.openai_provider.ChatOpenAI") as mock_chat:
            mock_llm = Mock()
            mock_chat.return_value = mock_llm

            provider = get_ai_provider()

            assert isinstance(provider, OpenAIProvider)
            assert not isinstance(provider, MockAIProvider)


@pytest.mark.asyncio
async def test_generate_completion_has_realistic_delay():
    """Test mock completion simulates realistic delay."""
    import time

    provider = MockAIProvider()
    messages = [{"role": "user", "content": "Test"}]

    start_time = time.time()
    await provider.generate_completion(messages)
    elapsed = time.time() - start_time

    # Should take between 0.5 and 1.5 seconds
    assert 0.4 < elapsed < 1.7  # Allow small margin


@pytest.mark.asyncio
async def test_mock_provider_supports_all_role_types():
    """Test mock provider has responses for all expected role types."""
    role_types = ["react", "python", "javascript", "fullstack"]

    for role_type in role_types:
        provider = MockAIProvider(role_type=role_type)
        messages = [{"role": "user", "content": "Test"}]

        response = await provider.generate_completion(messages)

        assert isinstance(response, str)
        assert len(response) > 0
