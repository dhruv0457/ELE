"""Local Development Configuration Override"""
from app.config import Settings as BaseSettings


class LocalSettings(BaseSettings):
    """Settings for local development without external dependencies"""
    
    # Override to use local SQLite instead of Supabase
    SUPABASE_URL: str = "sqlite:///./local.db"
    SUPABASE_ANON_KEY: str = "local-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "local-service-key"
    
    # Disable external services for local dev
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENCLAW_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    PORCUPINE_ACCESS_KEY: str = ""
    
    # Local data directory
    DATA_DIR: str = "~/.ele-agent-local"
    
    # Relaxed rate limits for local dev
    RATE_LIMIT_FREE_RPM: int = 1000
    RATE_LIMIT_PRO_RPM: int = 1000
    RATE_LIMIT_TEAM_RPM: int = 1000
    
    class Config:
        env_file = ".env.local"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Use local settings when running locally
import os
if os.getenv("ELE_LOCAL_DEV") == "1":
    settings = LocalSettings()
else:
    from app.config import settings