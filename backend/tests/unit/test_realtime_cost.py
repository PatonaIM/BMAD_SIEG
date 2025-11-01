"""Unit tests for Realtime API cost calculation."""

from decimal import Decimal

import pytest

from app.utils.realtime_cost import (
    calculate_realtime_cost,
    check_cost_threshold,
    estimate_interview_cost,
)


class TestCalculateRealtimeCost:
    """Test cost calculation for Realtime API usage."""
    
    def test_audio_only_cost(self):
        """Test cost calculation with only audio usage."""
        # 10 minutes input, 10 minutes output, no text tokens
        result = calculate_realtime_cost(
            input_audio_seconds=600,  # 10 minutes
            output_audio_seconds=600,  # 10 minutes
            input_text_tokens=0,
            output_text_tokens=0
        )
        
        # Input: 10 min * $0.06/min = $0.60
        # Output: 10 min * $0.24/min = $2.40
        # Total: $3.00
        assert result.input_audio_cost == Decimal("0.6000")
        assert result.output_audio_cost == Decimal("2.4000")
        assert result.input_text_cost == Decimal("0.0000")
        assert result.output_text_cost == Decimal("0.0000")
        assert result.total_cost == Decimal("3.0000")
    
    def test_text_only_cost(self):
        """Test cost calculation with only text tokens."""
        # No audio, 5000 input tokens, 10000 output tokens
        result = calculate_realtime_cost(
            input_audio_seconds=0,
            output_audio_seconds=0,
            input_text_tokens=5000,
            output_text_tokens=10000
        )
        
        # Input: 5000 tokens / 1000 * $0.01 = $0.05
        # Output: 10000 tokens / 1000 * $0.03 = $0.30
        # Total: $0.35
        assert result.input_audio_cost == Decimal("0.0000")
        assert result.output_audio_cost == Decimal("0.0000")
        assert result.input_text_cost == Decimal("0.0500")
        assert result.output_text_cost == Decimal("0.3000")
        assert result.total_cost == Decimal("0.3500")
    
    def test_combined_audio_and_text_cost(self):
        """Test cost calculation with both audio and text usage."""
        # 5 minutes input audio, 5 minutes output audio
        # 2500 input tokens, 7500 output tokens
        result = calculate_realtime_cost(
            input_audio_seconds=300,  # 5 minutes
            output_audio_seconds=300,  # 5 minutes
            input_text_tokens=2500,
            output_text_tokens=7500
        )
        
        # Audio: 5 * 0.06 + 5 * 0.24 = $1.50
        # Text: 2.5 * 0.01 + 7.5 * 0.03 = $0.25 + $0.225 = $0.2750
        # Total: $1.7750
        assert result.input_audio_cost == Decimal("0.3000")
        assert result.output_audio_cost == Decimal("1.2000")
        assert result.input_text_cost == Decimal("0.0250")
        assert result.output_text_cost == Decimal("0.2250")
        assert result.total_cost == Decimal("1.7500")
    
    def test_typical_20_minute_interview(self):
        """Test cost for typical 20-minute interview scenario."""
        # 10 minutes candidate speaking, 10 minutes AI speaking
        # Approx 100 tokens per minute: 1000 input, 1000 output
        result = calculate_realtime_cost(
            input_audio_seconds=600,  # 10 minutes
            output_audio_seconds=600,  # 10 minutes
            input_text_tokens=1000,
            output_text_tokens=1000
        )
        
        # Audio: 10 * 0.06 + 10 * 0.24 = $3.00
        # Text: 1 * 0.01 + 1 * 0.03 = $0.04
        # Total: $3.04
        assert result.total_cost == Decimal("3.0400")
        assert result.input_audio_minutes == Decimal("10.00")
        assert result.output_audio_minutes == Decimal("10.00")
    
    def test_fractional_seconds(self):
        """Test cost calculation with fractional seconds."""
        # 15.5 seconds input, 22.7 seconds output
        result = calculate_realtime_cost(
            input_audio_seconds=15.5,
            output_audio_seconds=22.7,
            input_text_tokens=100,
            output_text_tokens=150
        )
        
        # Should handle fractional minutes correctly
        assert result.input_audio_minutes == Decimal("0.26")  # 15.5/60 rounded
        assert result.output_audio_minutes == Decimal("0.38")  # 22.7/60 rounded
        assert result.total_cost > Decimal("0.0000")


class TestEstimateInterviewCost:
    """Test interview cost estimation."""
    
    def test_20_minute_interview_default_split(self):
        """Test 20-minute interview with default 50/50 speaking split."""
        cost = estimate_interview_cost(duration_minutes=20)
        
        # Should be approximately $3.04 for typical scenario
        assert Decimal("3.00") <= cost <= Decimal("3.20")
    
    def test_30_minute_interview_with_custom_split(self):
        """Test 30-minute interview with 60/40 candidate/AI split."""
        cost = estimate_interview_cost(
            duration_minutes=30,
            candidate_speaking_ratio=0.6
        )
        
        # Candidate speaks more (18 min), AI less (12 min)
        # Should be slightly less than 50/50 split (AI audio costs more)
        assert cost > Decimal("3.50")
        assert cost < Decimal("5.00")
    
    def test_5_minute_interview(self):
        """Test short 5-minute interview."""
        cost = estimate_interview_cost(duration_minutes=5)
        
        # Should be approximately 1/4 of 20-minute cost
        assert cost < Decimal("1.00")


class TestCheckCostThreshold:
    """Test cost threshold checking."""
    
    def test_below_threshold(self):
        """Test cost below default threshold."""
        assert check_cost_threshold(Decimal("3.50")) is False
        assert check_cost_threshold(Decimal("4.99")) is False
    
    def test_at_threshold(self):
        """Test cost exactly at threshold."""
        assert check_cost_threshold(Decimal("5.00")) is False
    
    def test_above_threshold(self):
        """Test cost above default threshold."""
        assert check_cost_threshold(Decimal("5.01")) is True
        assert check_cost_threshold(Decimal("10.00")) is True
    
    def test_custom_threshold(self):
        """Test with custom threshold."""
        assert check_cost_threshold(Decimal("2.50"), threshold=Decimal("3.00")) is False
        assert check_cost_threshold(Decimal("3.50"), threshold=Decimal("3.00")) is True
