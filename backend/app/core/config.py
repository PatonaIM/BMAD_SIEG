"""Application configuration using Pydantic settings."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database Components
    db_user: str
    db_password: str
    db_host: str
    db_port: int = 5432
    db_name: str

    # Test Database Components
    test_db_user: str
    test_db_password: str
    test_db_host: str
    test_db_port: int = 5432
    test_db_name: str

    # OpenAI API Configuration
    openai_api_key: SecretStr
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.7

    # OpenAI Speech Services Configuration (Whisper STT + TTS)
    # ================================================================
    # Text-to-Speech (TTS) Settings
    # ================================================================
    openai_tts_model: str = "tts-1"
    """
    OpenAI TTS model selection.
    Options:
    - "tts-1": Faster generation, good quality (recommended for MVP)
    - "tts-1-hd": Higher quality, slower generation (for production)
    Cost: $0.015 per 1,000 characters
    """

    openai_tts_voice: str = "alloy"
    """
    OpenAI TTS voice selection.
    Available voices:
    - "alloy": Neutral, professional (recommended default)
    - "echo": Clear, expressive
    - "fable": Warm, engaging  
    - "onyx": Deep, authoritative
    - "nova": Bright, energetic
    - "shimmer": Soft, whispery
    """

    openai_tts_speed: float = 1.0
    """
    Speech speed multiplier (0.25 - 4.0).
    Values:
    - 0.5: Half speed (slower, clearer)
    - 1.0: Normal speed (recommended)
    - 1.5: 1.5x faster (efficient)
    - 2.0: Double speed (for testing)
    """

    # ================================================================
    # Speech-to-Text (STT) Settings
    # ================================================================
    openai_stt_model: str = "whisper-1"
    """
    OpenAI Whisper model for speech transcription.
    Currently only "whisper-1" is available.
    Cost: $0.006 per minute of audio
    Accuracy: ~95% for clear English speech
    """

    openai_stt_language: str = "en"
    """
    Language code for speech transcription.
    Supported languages: en, es, fr, de, it, pt, nl, pl, ru, ja, ko, zh
    Setting correct language improves transcription accuracy.
    """

    # ================================================================
    # Audio Quality Constraints
    # ================================================================
    audio_max_file_size_mb: int = 25
    """
    Maximum audio file size in megabytes.
    OpenAI Whisper API hard limit: 25MB
    Typical 1-minute audio: ~1-3MB depending on quality
    """

    audio_min_sample_rate_hz: int = 16000
    """
    Minimum sample rate in Hz for good transcription quality.
    16kHz is sufficient for speech recognition.
    Higher rates (44.1kHz, 48kHz) provide better quality but larger files.
    """

    audio_min_duration_seconds: float = 0.1
    """
    Minimum audio duration in seconds.
    Rejects too-short audio clips that are likely noise or accidental recordings.
    """

    # ================================================================
    # Speech API Timeouts (seconds)
    # ================================================================
    speech_stt_timeout_seconds: int = 30
    """
    Timeout for Whisper transcription requests.
    30 seconds allows for processing of longer audio files.
    Typical processing time: 2-5 seconds for 1-minute audio.
    """

    speech_tts_timeout_seconds: int = 15
    """
    Timeout for TTS generation requests.
    15 seconds is sufficient for typical interview questions.
    Typical processing time: 1-3 seconds for 200-character text.
    """

    # ================================================================
    # OpenAI Realtime API Configuration
    # ================================================================
    enable_realtime_api: bool = True
    """
    Feature flag to enable/disable OpenAI Realtime API.
    When True: Use Realtime API for voice interviews (low latency)
    When False: Fall back to STT/TTS pipeline (Stories 1.5.3/1.5.4)
    
    Advantages of Realtime API:
    - Sub-1 second response latency vs. 10-15s with STT/TTS
    - Natural conversation flow with interruption support
    - Single WebSocket connection vs. multiple HTTP calls
    
    Trade-offs:
    - 2.5x higher cost ($3.80 vs $1.50 per 20-min interview)
    - Beta API (may have breaking changes)
    - Requires WebSocket support in infrastructure
    
    Default: True (production-ready as of v1.5.6)
    """

    realtime_api_model: str = "gpt-4o-realtime-preview-2024-10-01"
    """
    OpenAI Realtime API model.
    Current: gpt-4o-realtime-preview-2024-10-01 (beta)
    Update this when GA version is released.
    """

    realtime_voice: str = "alloy"
    """
    Voice for Realtime API audio output.
    Options: alloy, echo, fable, onyx, nova, shimmer
    Default: alloy (matches TTS default for consistency)
    """

    realtime_temperature: float = 0.7
    """
    Conversation temperature for Realtime API.
    Range: 0.0 (deterministic) to 1.0 (creative)
    Default: 0.7 (balanced, conversational)
    """

    realtime_max_response_tokens: int = 1000
    """
    Maximum tokens per AI response in Realtime API.
    Typical interview question: 50-200 tokens
    Default: 1000 (allows for detailed explanations)
    """

    # Development Settings
    use_mock_ai: bool = False

    # Supabase Storage Configuration
    supabase_url: str
    supabase_service_key: SecretStr
    supabase_anon_key: SecretStr | None = None
    video_retention_days: int = 30
    hard_delete_after_days: int = 90
    video_storage_threshold_gb: int = 100

    # Authentication
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Progressive Assessment Thresholds
    warmup_min_questions: int = 2
    warmup_confidence_threshold: float = 0.7
    standard_min_questions: int = 4
    standard_accuracy_threshold: float = 0.8
    boundary_confidence_threshold: float = 0.5

    # Progressive Assessment AI Timeouts (seconds)
    progressive_assessment_timeout: int = 30  # Timeout per AI call

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL URL from components."""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def test_database_url(self) -> str:
        """Construct async PostgreSQL URL for test database."""
        return (
            f"postgresql+asyncpg://{self.test_db_user}:{self.test_db_password}"
            f"@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}"
        )


# Global settings instance
settings = Settings()
