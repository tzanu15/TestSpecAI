"""
Configuration management for TestSpecAI backend.
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "TestSpecAI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    # AI Services
    LLM_SERVER_URL: str = "http://localhost:8001"
    NLP_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
