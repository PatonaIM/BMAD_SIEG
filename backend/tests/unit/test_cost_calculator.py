"""Unit tests for SpeechCostCalculator."""

from decimal import Decimal

import pytest

from app.utils.cost_calculator import SpeechCostCalculator


class TestSpeechCostCalculator:
    """Test cost calculation for STT and TTS services."""
    
    def test_calculate_stt_cost_60_seconds(self):
        """Test STT cost for exactly 1 minute."""
        cost = SpeechCostCalculator.calculate_stt_cost(60.0)
        assert cost == Decimal("0.0060")
    
    def test_calculate_stt_cost_90_seconds(self):
        """Test STT cost for 1.5 minutes."""
        cost = SpeechCostCalculator.calculate_stt_cost(90.0)
        assert cost == Decimal("0.0090")
    
    def test_calculate_stt_cost_300_seconds(self):
        """Test STT cost for 5 minutes."""
        cost = SpeechCostCalculator.calculate_stt_cost(300.0)
        assert cost == Decimal("0.0300")
    
    def test_calculate_stt_cost_zero(self):
        """Test STT cost for zero duration."""
        cost = SpeechCostCalculator.calculate_stt_cost(0.0)
        assert cost == Decimal("0.0000")
    
    def test_calculate_stt_cost_negative(self):
        """Test STT cost for negative duration."""
        cost = SpeechCostCalculator.calculate_stt_cost(-10.0)
        assert cost == Decimal("0.0000")
    
    def test_calculate_tts_cost_1000_chars(self):
        """Test TTS cost for exactly 1000 characters."""
        text = "A" * 1000
        cost = SpeechCostCalculator.calculate_tts_cost(text)
        assert cost == Decimal("0.0150")
    
    def test_calculate_tts_cost_2500_chars(self):
        """Test TTS cost for 2500 characters."""
        text = "A" * 2500
        cost = SpeechCostCalculator.calculate_tts_cost(text)
        assert cost == Decimal("0.0375")
    
    def test_calculate_tts_cost_empty(self):
        """Test TTS cost for empty text."""
        cost = SpeechCostCalculator.calculate_tts_cost("")
        assert cost == Decimal("0.0000")
    
    def test_calculate_tts_cost_small_text(self):
        """Test TTS cost for small text (< 1000 chars)."""
        text = "Hello world"  # 11 chars
        cost = SpeechCostCalculator.calculate_tts_cost(text)
        # Should be rounded to 4 decimal places
        expected = Decimal("0.0002")  # 11 / 1000 * 0.015 = 0.000165 -> 0.0002
        assert cost == expected
    
    def test_calculate_total_speech_cost(self):
        """Test total speech cost calculation."""
        # 2 minutes STT + 2000 chars TTS
        total = SpeechCostCalculator.calculate_total_speech_cost(
            stt_duration_seconds=120.0,
            tts_text="A" * 2000
        )
        # STT: 120/60 * 0.006 = 0.012
        # TTS: 2000/1000 * 0.015 = 0.030
        # Total: 0.042
        assert total == Decimal("0.0420")
