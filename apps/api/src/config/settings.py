"""
Application Settings — CognitiveOS API
Uses pydantic-settings for environment-validated configuration.
"""
from functools import lru_cache
from typing import List, Any, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


import os
from pathlib import Path

# Resolve root .env path dynamically (three levels up from src/config)
ROOT_ENV_PATH = Path(__file__).resolve().parent.parent.parent.parent / ".env"
ENV_FILE = str(ROOT_ENV_PATH) if ROOT_ENV_PATH.exists() else ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        protected_namespaces=(),
    )

    # ── Application ────────────────────────────────────────────
    ENV: str = Field(default="development")
    APP_NAME: str = Field(default="CognitiveOS")
    API_VERSION: str = Field(default="v1")
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_SECRET_KEY: str = Field(default="change-me-in-production")
    DEBUG: bool = Field(default=False)

    # ── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS: Any = Field(default="*")

    # ── OpenAI / Groq ──────────────────────────────────────────
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_API_BASE: str = Field(default="https://api.openai.com/v1")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    OPENAI_MAX_TOKENS: int = Field(default=4096)
    OPENAI_TEMPERATURE: float = Field(default=0.3)

    # ── PostgreSQL ────────────────────────────────────────────
    # FORCE ASYNCPG DRIVER
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cognitive_user:password@localhost:5432/cognitive_os"
    )
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_TTL_SECONDS: int = Field(default=3600)

    # ── Pipeline ──────────────────────────────────────────────
    PIPELINE_TIMEOUT_MS: int = Field(default=30000)
    PIPELINE_MAX_RETRIES: int = Field(default=2)
    ENABLE_REFLECTION_ENGINE: bool = Field(default=True)
    ENABLE_VOCABULARY_EXPANSION: bool = Field(default=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
