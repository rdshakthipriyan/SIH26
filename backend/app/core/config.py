"""
Configuration management for MediKiosk backend.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Database
    DATABASE_URL: str = "sqlite:///./medikiosk.db"

    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 43200

    # Environment
    ENVIRONMENT: str = "development"

    # Speech Recognition
    SPEECH_PROVIDER: str = "mock"
    SARVAM_API_KEY: Optional[str] = None

    # Text-to-Speech
    TTS_PROVIDER: str = "mock"

    # OCR
    OCR_PROVIDER: str = "mock"
    VISION_API_KEY: Optional[str] = None

    # ABHA / ABDM
    ABHA_PROVIDER: str = "mock"
    ABDM_PROVIDER: str = "mock"

    # Queue
    QUEUE_PROVIDER: str = "mock"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174"]

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_MIME_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "application/pdf"
    ]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @property
    def max_upload_size_bytes(self) -> int:
        """Convert MB to bytes for file upload validation."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
