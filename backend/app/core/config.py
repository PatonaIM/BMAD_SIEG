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
    openai_tts_model: str = "tts-1"  # Options: "tts-1" (faster) or "tts-1-hd" (higher quality)
    openai_tts_voice: str = "alloy"  # Options: alloy, echo, fable, onyx, nova, shimmer
    openai_tts_speed: float = 1.0  # Speed multiplier: 0.25 to 4.0
    openai_stt_model: str = "whisper-1"  # OpenAI Whisper model
    openai_stt_language: str = "en"  # Language code for STT (en, es, fr, etc.)
    
    # Audio Quality Constraints
    audio_max_file_size_mb: int = 25  # OpenAI Whisper API file size limit
    audio_min_sample_rate_hz: int = 16000  # Minimum sample rate for good transcription quality
    audio_min_duration_seconds: float = 0.1  # Reject too-short audio clips
    
    # Speech API Timeouts (seconds)
    speech_stt_timeout_seconds: int = 30  # Whisper transcription timeout
    speech_tts_timeout_seconds: int = 15  # TTS generation timeout

    # Development Settings
    use_mock_ai: bool = False

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
