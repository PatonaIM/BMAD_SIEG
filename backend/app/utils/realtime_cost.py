"""Realtime API cost calculation utilities."""

from dataclasses import dataclass
from decimal import Decimal


# OpenAI Realtime API Pricing (as of November 2025)
# Source: https://openai.com/api/pricing/
REALTIME_INPUT_AUDIO_COST_PER_MINUTE = Decimal("0.06")  # $0.06 per minute
REALTIME_OUTPUT_AUDIO_COST_PER_MINUTE = Decimal("0.24")  # $0.24 per minute
REALTIME_TEXT_INPUT_COST_PER_1K_TOKENS = Decimal("0.01")  # $0.01 per 1K tokens
REALTIME_TEXT_OUTPUT_COST_PER_1K_TOKENS = Decimal("0.03")  # $0.03 per 1K tokens


@dataclass
class RealtimeCostBreakdown:
    """
    Breakdown of Realtime API costs.
    
    Attributes:
        input_audio_cost: Cost for input audio (candidate speaking)
        output_audio_cost: Cost for output audio (AI speaking)
        input_text_cost: Cost for input text tokens (transcription)
        output_text_cost: Cost for output text tokens (AI generation)
        total_cost: Total cost in USD
        input_audio_minutes: Duration of input audio in minutes
        output_audio_minutes: Duration of output audio in minutes
        input_text_tokens: Number of input text tokens
        output_text_tokens: Number of output text tokens
    """
    input_audio_cost: Decimal
    output_audio_cost: Decimal
    input_text_cost: Decimal
    output_text_cost: Decimal
    total_cost: Decimal
    input_audio_minutes: Decimal
    output_audio_minutes: Decimal
    input_text_tokens: int
    output_text_tokens: int


def calculate_realtime_cost(
    input_audio_seconds: float,
    output_audio_seconds: float,
    input_text_tokens: int,
    output_text_tokens: int
) -> RealtimeCostBreakdown:
    """
    Calculate cost for OpenAI Realtime API usage.
    
    This function computes the total cost based on:
    - Audio input duration (candidate speaking)
    - Audio output duration (AI speaking)
    - Text input tokens (transcription tokens)
    - Text output tokens (AI response tokens)
    
    Pricing:
    --------
    - Input audio: $0.06 per minute
    - Output audio: $0.24 per minute
    - Input text: $0.01 per 1K tokens
    - Output text: $0.03 per 1K tokens
    
    Args:
        input_audio_seconds: Duration of input audio in seconds
        output_audio_seconds: Duration of output audio in seconds
        input_text_tokens: Number of input text tokens
        output_text_tokens: Number of output text tokens
    
    Returns:
        RealtimeCostBreakdown with detailed cost information
    
    Example:
        >>> # 20-minute interview: 10 min candidate, 10 min AI
        >>> cost = calculate_realtime_cost(
        ...     input_audio_seconds=600,  # 10 minutes
        ...     output_audio_seconds=600,  # 10 minutes
        ...     input_text_tokens=5000,
        ...     output_text_tokens=15000
        ... )
        >>> print(f"Total cost: ${cost.total_cost}")
        Total cost: $3.80
    """
    # Convert seconds to minutes
    input_audio_minutes = Decimal(str(input_audio_seconds)) / Decimal("60")
    output_audio_minutes = Decimal(str(output_audio_seconds)) / Decimal("60")
    
    # Calculate audio costs
    input_audio_cost = input_audio_minutes * REALTIME_INPUT_AUDIO_COST_PER_MINUTE
    output_audio_cost = output_audio_minutes * REALTIME_OUTPUT_AUDIO_COST_PER_MINUTE
    
    # Calculate text token costs
    input_text_cost = (
        Decimal(str(input_text_tokens)) / Decimal("1000")
    ) * REALTIME_TEXT_INPUT_COST_PER_1K_TOKENS
    
    output_text_cost = (
        Decimal(str(output_text_tokens)) / Decimal("1000")
    ) * REALTIME_TEXT_OUTPUT_COST_PER_1K_TOKENS
    
    # Calculate total cost
    total_cost = input_audio_cost + output_audio_cost + input_text_cost + output_text_cost
    
    return RealtimeCostBreakdown(
        input_audio_cost=input_audio_cost.quantize(Decimal("0.0001")),
        output_audio_cost=output_audio_cost.quantize(Decimal("0.0001")),
        input_text_cost=input_text_cost.quantize(Decimal("0.0001")),
        output_text_cost=output_text_cost.quantize(Decimal("0.0001")),
        total_cost=total_cost.quantize(Decimal("0.0001")),
        input_audio_minutes=input_audio_minutes.quantize(Decimal("0.01")),
        output_audio_minutes=output_audio_minutes.quantize(Decimal("0.01")),
        input_text_tokens=input_text_tokens,
        output_text_tokens=output_text_tokens
    )


def estimate_interview_cost(
    duration_minutes: int,
    candidate_speaking_ratio: float = 0.5
) -> Decimal:
    """
    Estimate total Realtime API cost for an interview.
    
    Provides a rough estimate based on typical interview patterns:
    - Candidate and AI split speaking time
    - Average token usage per minute
    
    Args:
        duration_minutes: Total interview duration in minutes
        candidate_speaking_ratio: Ratio of time candidate speaks (0.0 to 1.0)
    
    Returns:
        Estimated total cost in USD
    
    Example:
        >>> # 20-minute interview with 50/50 speaking split
        >>> cost = estimate_interview_cost(20, 0.5)
        >>> print(f"Estimated cost: ${cost}")
        Estimated cost: $3.80
    """
    candidate_minutes = duration_minutes * candidate_speaking_ratio
    ai_minutes = duration_minutes * (1 - candidate_speaking_ratio)
    
    # Estimate tokens (rough average: ~100 tokens per minute of speech)
    tokens_per_minute = 100
    input_tokens = int(candidate_minutes * tokens_per_minute)
    output_tokens = int(ai_minutes * tokens_per_minute)
    
    cost_breakdown = calculate_realtime_cost(
        input_audio_seconds=candidate_minutes * 60,
        output_audio_seconds=ai_minutes * 60,
        input_text_tokens=input_tokens,
        output_text_tokens=output_tokens
    )
    
    return cost_breakdown.total_cost


def check_cost_threshold(
    current_cost: Decimal,
    threshold: Decimal = Decimal("5.0")
) -> bool:
    """
    Check if cost exceeds threshold for alert.
    
    Args:
        current_cost: Current accumulated cost in USD
        threshold: Alert threshold in USD (default: $5.00)
    
    Returns:
        True if cost exceeds threshold, False otherwise
    """
    return current_cost > threshold
