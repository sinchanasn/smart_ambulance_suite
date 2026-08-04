import os
from typing import List, Union
# pyrefly: ignore [missing-import]
from pydantic import AnyHttpUrl, field_validator
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings and Environment Configuration."""

    PROJECT_NAME: str = "Smart Ambulance Suite API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True
    SECRET_KEY: str = "super-secret-key-change-in-production-environment"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "*",
    ]

    # Database Settings (PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/smart_ambulance_db"

    # Firebase Settings Placeholders
    FIREBASE_PROJECT_ID: str = "smart-ambulance-suite"
    FIREBASE_PRIVATE_KEY_PATH: str = "path/to/firebase-credentials.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
