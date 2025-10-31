"""Cost calculation utilities for speech services (STT/TTS)."""

from decimal import Decimal, ROUND_HALF_UP


class SpeechCostCalculator:
    """
    Calculate costs for speech services (STT and TTS).
    
    Pricing (as of October 2025):
    - Whisper STT: $0.006 per minute of audio
    - TTS: $0.015 per 1,000 characters
    
    All costs are returned as Decimal with 4 decimal places for precise
    financial tracking and database storage.
    
    Usage:
        calculator = SpeechCostCalculator()
        
        # STT cost for 90 seconds of audio
        stt_cost = calculator.calculate_stt_cost(90.0)
        print(stt_cost)  # Decimal('0.0090')
        
        # TTS cost for 2500 characters
        tts_cost = calculator.calculate_tts_cost("..." * 833)  # 2500 chars
        print(tts_cost)  # Decimal('0.0375')
    """
    
    # OpenAI Whisper pricing: $0.006 per minute
    STT_COST_PER_MINUTE = Decimal("0.006")
    
    # OpenAI TTS pricing: $0.015 per 1,000 characters
    TTS_COST_PER_1K_CHARS = Decimal("0.015")
    
    @classmethod
    def calculate_stt_cost(cls, duration_seconds: float) -> Decimal:
        """
        Calculate speech-to-text cost based on audio duration.
        
        Formula: (duration_seconds / 60) * $0.006
        
        Args:
            duration_seconds: Audio duration in seconds (e.g., 90.5)
        
        Returns:
            Decimal: Cost in USD rounded to 4 decimal places (e.g., Decimal('0.0090'))
        
        Examples:
            >>> SpeechCostCalculator.calculate_stt_cost(60.0)
            Decimal('0.0060')  # 1 minute = $0.006
            
            >>> SpeechCostCalculator.calculate_stt_cost(90.0)
            Decimal('0.0090')  # 1.5 minutes = $0.009
            
            >>> SpeechCostCalculator.calculate_stt_cost(300.0)
            Decimal('0.0300')  # 5 minutes = $0.030
            
            >>> SpeechCostCalculator.calculate_stt_cost(0.0)
            Decimal('0.0000')  # No audio = $0
        """
        if duration_seconds <= 0:
            return Decimal("0.0000")
        
        # Convert seconds to minutes
        duration_minutes = Decimal(str(duration_seconds)) / Decimal("60")
        
        # Calculate cost
        cost = duration_minutes * cls.STT_COST_PER_MINUTE
        
        # Round to 4 decimal places
        return cost.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    
    @classmethod
    def calculate_tts_cost(cls, text: str) -> Decimal:
        """
        Calculate text-to-speech cost based on character count.
        
        Formula: (character_count / 1000) * $0.015
        
        Args:
            text: Text to be synthesized (e.g., "Hello world")
        
        Returns:
            Decimal: Cost in USD rounded to 4 decimal places (e.g., Decimal('0.0150'))
        
        Examples:
            >>> SpeechCostCalculator.calculate_tts_cost("Hello")
            Decimal('0.0001')  # 5 chars = $0.000075 rounded to $0.0001
            
            >>> SpeechCostCalculator.calculate_tts_cost("A" * 1000)
            Decimal('0.0150')  # 1000 chars = $0.015
            
            >>> SpeechCostCalculator.calculate_tts_cost("A" * 2500)
            Decimal('0.0375')  # 2500 chars = $0.0375
            
            >>> SpeechCostCalculator.calculate_tts_cost("")
            Decimal('0.0000')  # Empty text = $0
        """
        if not text:
            return Decimal("0.0000")
        
        # Get character count
        char_count = Decimal(str(len(text)))
        
        # Calculate cost per 1000 characters
        cost = (char_count / Decimal("1000")) * cls.TTS_COST_PER_1K_CHARS
        
        # Round to 4 decimal places
        return cost.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    
    @classmethod
    def calculate_total_speech_cost(
        cls,
        stt_duration_seconds: float,
        tts_text: str
    ) -> Decimal:
        """
        Calculate total speech cost for both STT and TTS operations.
        
        Convenience method for calculating combined costs when both
        transcription and synthesis are used in a single interaction.
        
        Args:
            stt_duration_seconds: Audio duration for transcription
            tts_text: Text for synthesis
        
        Returns:
            Decimal: Total cost in USD rounded to 4 decimal places
        
        Example:
            >>> calculator = SpeechCostCalculator()
            >>> total = calculator.calculate_total_speech_cost(
            ...     stt_duration_seconds=120.0,  # 2 minutes
            ...     tts_text="A" * 2000           # 2000 chars
            ... )
            >>> print(total)
            Decimal('0.0420')  # $0.012 (STT) + $0.030 (TTS)
        """
        stt_cost = cls.calculate_stt_cost(stt_duration_seconds)
        tts_cost = cls.calculate_tts_cost(tts_text)
        
        total = stt_cost + tts_cost
        return total.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
