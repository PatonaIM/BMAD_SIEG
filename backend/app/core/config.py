"""Application configuration using Pydantic settings."""

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

    # OpenAI API (for later stories)
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # Authentication
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"

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
