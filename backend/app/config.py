"""Configuration Management"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ELE Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database (SQLite for local, PostgreSQL for production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./ele_agent.db"

    # Supabase (Optional for local dev, required for cloud sync)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # Auth
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24

    # API Keys (Platform)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    OPENCLAW_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None

    # Voice
    PORCUPINE_ACCESS_KEY: Optional[str] = None
    VOSK_MODEL_PATH: str = "~/.ele-agent/vosk-model"

    # Monitoring
    SENTRY_DSN: Optional[str] = None

    # Storage
    DATA_DIR: str = "~/.ele-agent"

    # Rate Limiting
    RATE_LIMIT_FREE_RPM: int = 30
    RATE_LIMIT_PRO_RPM: int = 120
    RATE_LIMIT_TEAM_RPM: int = 300

    # Credits
    FREE_CREDITS_DAILY: int = 100
    PRO_CREDITS_DAILY: int = 1000
    TEAM_CREDITS_DAILY: int = 5000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()