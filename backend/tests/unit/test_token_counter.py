"""Unit tests for token counter utilities."""

from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from app.utils.token_counter import (
    count_tokens_for_messages,
    count_tokens_for_text,
    estimate_cost,
    estimate_interview_cost,
    get_model_pricing,
)


@patch("app.utils.token_counter.tiktoken.encoding_for_model")
def test_count_tokens_for_messages(mock_encoding):
    """Test counting tokens for messages."""
    mock_enc = Mock()
    mock_enc.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens per field
    mock_encoding.return_value = mock_enc

    messages = [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello"},
    ]

    count = count_tokens_for_messages(messages, "gpt-4o-mini")

    assert count > 0
    assert isinstance(count, int)


def test_estimate_cost_gpt4o_mini():
    """Test cost estimation for GPT-4o-mini."""
    cost = estimate_cost(1000, 500, "gpt-4o-mini")

    assert isinstance(cost, Decimal)
    assert cost > 0
    # 1000 input tokens * $0.150/1M + 500 output tokens * $0.600/1M
    expected = Decimal("0.00045")
    assert abs(cost - expected) < Decimal("0.000001")


def test_estimate_cost_gpt4():
    """Test cost estimation for GPT-4."""
    cost = estimate_cost(1000, 500, "gpt-4")

    assert isinstance(cost, Decimal)
    assert cost > 0
    # 1000 * $30/1M + 500 * $60/1M
    expected = Decimal("0.06")
    assert abs(cost - expected) < Decimal("0.001")


def test_estimate_cost_unknown_model():
    """Test cost estimation for unknown model (defaults to gpt-4o-mini)."""
    cost = estimate_cost(1000, 500, "unknown-model")

    assert isinstance(cost, Decimal)
    assert cost > 0


@patch("app.utils.token_counter.tiktoken.encoding_for_model")
def test_count_tokens_for_text(mock_encoding):
    """Test counting tokens in plain text."""
    mock_enc = Mock()
    mock_enc.encode.return_value = [1, 2, 3, 4, 5, 6, 7, 8]  # 8 tokens
    mock_encoding.return_value = mock_enc

    text = "This is a test message."
    count = count_tokens_for_text(text, "gpt-4o-mini")

    assert count == 8
    mock_enc.encode.assert_called_once_with(text)


def test_get_model_pricing_gpt4o_mini():
    """Test getting pricing for GPT-4o-mini."""
    pricing = get_model_pricing("gpt-4o-mini")

    assert "input" in pricing
    assert "output" in pricing
    assert pricing["input"] == Decimal("0.150")
    assert pricing["output"] == Decimal("0.600")


def test_get_model_pricing_gpt4():
    """Test getting pricing for GPT-4."""
    pricing = get_model_pricing("gpt-4")

    assert pricing["input"] == Decimal("30.00")
    assert pricing["output"] == Decimal("60.00")


def test_get_model_pricing_unknown():
    """Test getting pricing for unknown model."""
    with pytest.raises(KeyError):
        get_model_pricing("unknown-model")


def test_estimate_interview_cost():
    """Test estimating interview cost."""
    cost = estimate_interview_cost(
        avg_message_length=100,
        message_count=20,
        model="gpt-4o-mini"
    )

    assert isinstance(cost, Decimal)
    assert cost > 0
    # Should be a reasonable cost for 20 exchanges


def test_estimate_interview_cost_gpt4():
    """Test estimating interview cost with GPT-4."""
    cost_mini = estimate_interview_cost(100, 20, "gpt-4o-mini")
    cost_gpt4 = estimate_interview_cost(100, 20, "gpt-4")

    # GPT-4 should be significantly more expensive
    assert cost_gpt4 > cost_mini
    assert cost_gpt4 > cost_mini * 100  # At least 100x more expensive
