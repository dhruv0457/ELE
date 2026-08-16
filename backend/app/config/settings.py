"""Configuration Management with Pydantic + TOML"""
import os
import tomli
import tomli_w
from pathlib import Path
from typing import Any, Optional, Dict, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderConfig(BaseSettings):
    enabled: bool = True
    model: str
    priority: int = 5

    class Config:
        extra = "allow"


class VoiceWakeWordConfig(BaseSettings):
    enabled: bool = True
    sensitivity: str = "medium"
    keyword: str = "hey ellie"
    access_key: str = ""

    class Config:
        extra = "allow"


class VoiceSTTConfig(BaseSettings):
    engine: str = "auto"
    whisper_model: str = "whisper-1"
    vosk_model_path: str = "~/.ele-agent/voice/vosk-model"

    class Config:
        extra = "allow"


class VoiceTTSConfig(BaseSettings):
    engine: str = "auto"
    voice: str = "jarvis"
    speed: float = 1.0
    volume: float = 1.0

    class Config:
        extra = "allow"


class VoiceVADConfig(BaseSettings):
    engine: str = "silero"
    silence_timeout_ms: int = 500
    min_speech_ms: int = 100

    class Config:
        extra = "allow"


class VoiceConfig(BaseSettings):
    wake_word: VoiceWakeWordConfig = Field(default_factory=VoiceWakeWordConfig)
    stt: VoiceSTTConfig = Field(default_factory=VoiceSTTConfig)
    tts: VoiceTTSConfig = Field(default_factory=VoiceTTSConfig)
    vad: VoiceVADConfig = Field(default_factory=VoiceVADConfig)

    class Config:
        extra = "allow"


class ToolsFileConfig(BaseSettings):
    enabled: bool = True
    confirm_write: bool = True
    confirm_delete: bool = True

    class Config:
        extra = "allow"


class ToolsShellConfig(BaseSettings):
    enabled: bool = True
    confirm_all: bool = True
    timeout: int = 120

    class Config:
        extra = "allow"


class ToolsBrowserConfig(BaseSettings):
    enabled: bool = True
    headless: bool = False
    stealth: bool = True
    timeout: int = 30

    class Config:
        extra = "allow"


class ToolsAppLaunchConfig(BaseSettings):
    enabled: bool = True
    whitelist: List[str] = Field(default_factory=lambda: ["code", "chrome", "firefox", "notepad", "explorer", "terminal"])

    class Config:
        extra = "allow"


class ToolsEmailConfig(BaseSettings):
    enabled: bool = False
    confirm_send: bool = True

    class Config:
        extra = "allow"


class ToolsCalendarConfig(BaseSettings):
    enabled: bool = False
    confirm_write: bool = True

    class Config:
        extra = "allow"


class ToolsConfig(BaseSettings):
    file: ToolsFileConfig = Field(default_factory=ToolsFileConfig)
    shell: ToolsShellConfig = Field(default_factory=ToolsShellConfig)
    browser: ToolsBrowserConfig = Field(default_factory=ToolsBrowserConfig)
    app_launch: ToolsAppLaunchConfig = Field(default_factory=ToolsAppLaunchConfig)
    email: ToolsEmailConfig = Field(default_factory=ToolsEmailConfig)
    calendar: ToolsCalendarConfig = Field(default_factory=ToolsCalendarConfig)

    class Config:
        extra = "allow"


class MemoryShortTermConfig(BaseSettings):
    dynamic: bool = True
    max_turns: int = 50

    class Config:
        extra = "allow"


class MemoryLongTermConfig(BaseSettings):
    enabled: bool = True
    index_path: str = "~/.ele-agent/memory/faiss"
    embedding_model: str = "bge-small"

    class Config:
        extra = "allow"


class MemoryEpisodicConfig(BaseSettings):
    enabled: bool = True
    db_path: str = "~/.ele-agent/memory/episodic.db"
    retention: str = "forever"
    dedup: bool = True

    class Config:
        extra = "allow"


class MemoryProjectConfig(BaseSettings):
    enabled: bool = True
    watch_paths: List[str] = Field(default_factory=lambda: ["~/projects"])
    marker_files: List[str] = Field(default_factory=lambda: ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git"])

    class Config:
        extra = "allow"


class MemoryConfig(BaseSettings):
    short_term: MemoryShortTermConfig = Field(default_factory=MemoryShortTermConfig)
    long_term: MemoryLongTermConfig = Field(default_factory=MemoryLongTermConfig)
    episodic: MemoryEpisodicConfig = Field(default_factory=MemoryEpisodicConfig)
    project: MemoryProjectConfig = Field(default_factory=MemoryProjectConfig)

    class Config:
        extra = "allow"


class PluginsConfig(BaseSettings):
    auto_update: bool = True
    allow_community: bool = True
    install_path: str = "~/.ele-agent/plugins"
    marketplace_url: str = "https://api.ele-agent.dev/api/v1/plugins/marketplace"
    templates: List[str] = Field(default_factory=lambda: ["python", "json", "wasm"])

    class Config:
        extra = "allow"


class SecurityConfig(BaseSettings):
    encryption: str = "age"
    kdf: str = "hardware"
    keyring_backend: str = "auto"

    class Config:
        extra = "allow"


class UIConfig(BaseSettings):
    status_bar: List[str] = Field(default_factory=lambda: ["connection", "model", "credits", "battery", "voice", "time"])
    command_palette: str = "full"
    notifications: str = "sidebar_badge"
    mouse_support: bool = True
    animations: bool = True
    animation_fps: int = 60
    theme_preview: str = "pane"
    hidden_files_toggle: str = "ctrl+h"
    editor_autosave: bool = True
    shell_pager: str = "builtin"
    browser_stealth: bool = True
    diff_view: str = "both"
    terminal_emulator: bool = True
    rag_reindex: str = "session_start"
    session_export: str = "markdown"

    class Config:
        extra = "allow"


class LoggingConfig(BaseSettings):
    level: str = "INFO"
    format: str = "json"
    rotation: str = "daily"
    retention_days: int = 30
    per_module: bool = True

    class Config:
        extra = "allow"


class AdvancedConfig(BaseSettings):
    startup_timeout: int = 2
    hot_reload: bool = True
    lazy_load: bool = True
    accessibility: str = "full"

    class Config:
        extra = "allow"


class BackendConfig(BaseSettings):
    host: str = "localhost"
    port: int = 8000
    ws_path: str = "/api/v1/ws/chat"
    auto_start: bool = True
    timeout_seconds: int = 30

    class Config:
        extra = "allow"


class LLMConfig(BaseSettings):
    default_model: str = "auto"
    max_parallel: int = 8
    timeout_seconds: int = 60
    temperature: float = 0.7
    max_tokens: int = 4096
    providers: Dict[str, LLMProviderConfig] = Field(default_factory=dict)

    class Config:
        extra = "allow"


class AppConfig(BaseSettings):
    theme: str = "tokyo-night"
    language: str = "en"
    auto_update: bool = True
    start_minimized: bool = False
    telemetry: str = "errors"
    version: str = "1.0.0"

    class Config:
        extra = "allow"


class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    backend: BackendConfig = Field(default_factory=BackendConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    plugins: PluginsConfig = Field(default_factory=PluginsConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)

    # Environment variables (loaded from .env)
    DATABASE_URL: str = "sqlite+aiosqlite:///~/.ele-agent/sessions.db"
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    NVIDIA_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    PORCUPINE_ACCESS_KEY: Optional[str] = None
    VOSK_MODEL_PATH: str = "~/.ele-agent/voice/vosk-model"
    SENTRY_DSN: Optional[str] = None
    DATA_DIR: str = "~/.ele-agent"
    DEBUG: bool = True
    RATE_LIMIT_FREE_RPM: int = 30
    RATE_LIMIT_PRO_RPM: int = 120
    RATE_LIMIT_TEAM_RPM: int = 300
    FREE_CREDITS_DAILY: int = 100
    PRO_CREDITS_DAILY: int = 1000
    TEAM_CREDITS_DAILY: int = 5000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
        env_nested_delimiter="__",
    )

    def __init__(self, **kwargs):
        # Load TOML config first, then env vars override
        toml_config = self._load_toml_config()
        merged = {**toml_config, **kwargs}
        super().__init__(**merged)

    def _load_toml_config(self) -> Dict[str, Any]:
        config_path = self._get_config_path()
        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    return tomli.load(f)
            except Exception:
                pass
        return {}

    def _get_config_path(self) -> Path:
        if os.name == "nt":
            return Path(os.environ.get("USERPROFILE", "~")) / ".ele-agent" / "config.toml"
        return Path.home() / ".ele-agent" / "config.toml"

    def save_toml(self):
        """Save current config to TOML file"""
        config_path = self._get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.model_dump(exclude_none=True)
        # Remove env-only fields
        env_fields = {
            "DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY",
            "JWT_SECRET", "JWT_ALGORITHM", "JWT_EXPIRY_HOURS",
            "OPENAI_API_KEY", "GEMINI_API_KEY", "GROQ_API_KEY", "NVIDIA_API_KEY", "ANTHROPIC_API_KEY",
            "PORCUPINE_ACCESS_KEY", "VOSK_MODEL_PATH", "SENTRY_DSN",
            "DATA_DIR", "RATE_LIMIT_FREE_RPM", "RATE_LIMIT_PRO_RPM", "RATE_LIMIT_TEAM_RPM",
            "FREE_CREDITS_DAILY", "PRO_CREDITS_DAILY", "TEAM_CREDITS_DAILY",
        }
        for field in env_fields:
            data.pop(field, None)
        with open(config_path, "wb") as f:
            tomli_w.dump(data, f)

    def get_llm_provider_config(self, provider: str) -> Optional[LLMProviderConfig]:
        return self.llm.providers.get(provider)

    def get_available_providers(self) -> List[str]:
        providers = []
        for name, config in self.llm.providers.items():
            if config.enabled:
                # Check if user key or platform key exists
                env_key = f"{name.upper()}_API_KEY"
                if getattr(self, env_key, None) or config.enabled:
                    providers.append(name)
        return providers


# Global settings instance
settings = Settings()

# Default LLM providers configuration
DEFAULT_PROVIDERS = {
    "gemini": {"model": "gemini-1.5-pro", "priority": 1},
    "groq": {"model": "llama-3.1-70b-versatile", "priority": 2},
    "nvidia": {"model": "nemotron-3-ultra", "priority": 3},
    "claude": {"model": "claude-3-5-sonnet", "priority": 4},
    "openai": {"model": "gpt-4o", "priority": 5},
}

# Initialize default providers if not set
if not settings.llm.providers:
    settings.llm.providers = {
        name: LLMProviderConfig(**config)
        for name, config in DEFAULT_PROVIDERS.items()
    }