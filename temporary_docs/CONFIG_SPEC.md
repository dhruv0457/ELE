# Configuration Specification (TOML)

## File Locations

| Platform | Path |
|----------|------|
| Windows | `%USERPROFILE%\.ele-agent\config.toml` |
| macOS | `~/.ele-agent/config.toml` |
| Linux | `~/.ele-agent/config.toml` |

## Environment Variables (`.env`)

```bash
# Platform API Keys (for credit fallback)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AI...
GROQ_API_KEY=gsk_...
NVIDIA_API_KEY=nvapi-...
ANTHROPIC_API_KEY=sk-ant-...

# Voice
PORCUPINE_ACCESS_KEY=...

# Monitoring (optional)
SENTRY_DSN=...
```

## Config File Schema (config.toml)

```toml
# =============================================================================
# ELE Agent Configuration
# =============================================================================

[app]
theme = "tokyo-night"           # One of: tokyo-night, catppuccin, dracula, gruvbox, nord, solarized, one-dark, monokai, github-dark, custom
language = "en"                 # English only (v1)
auto_update = true              # Check for updates on startup
start_minimized = false         # Start in system tray
telemetry = "errors"            # full, errors, none

[backend]
host = "localhost"
port = 8000
ws_path = "/api/v1/ws/chat"
auto_start = true               # Spawn uvicorn subprocess on CLI start
timeout_seconds = 30            # Backend startup timeout

[llm]
default_model = "auto"          # auto, gemini, groq, nvidia, claude, gpt
max_parallel = 8                # Max concurrent LLM calls
timeout_seconds = 60            # Per-request timeout
temperature = 0.7               # Default temperature
max_tokens = 4096               # Default max tokens

[llm.providers]
# User keys (BYOK) - stored encrypted in Age keyring
# Platform keys - from .env
gemini = { enabled = true, model = "gemini-1.5-pro", priority = 1 }
groq = { enabled = true, model = "llama-3.1-70b-versatile", priority = 2 }
nvidia = { enabled = true, model = "nemotron-3-ultra", priority = 3 }
claude = { enabled = true, model = "claude-3-5-sonnet", priority = 4 }
openai = { enabled = true, model = "gpt-4o", priority = 5 }

[tools]
file = { enabled = true, confirm_write = true, confirm_delete = true }
shell = { enabled = true, confirm_all = true, timeout = 120 }
browser = { enabled = true, headless = false, stealth = true, timeout = 30 }
app_launch = { enabled = true, whitelist = ["code", "chrome", "firefox", "notepad", "explorer", "terminal"] }
email = { enabled = false, confirm_send = true }
calendar = { enabled = false, confirm_write = true }

[voice]
wake_word = { enabled = true, sensitivity = "medium", keyword = "hey ellie" }
stt = { engine = "auto", whisper_model = "whisper-1", vosk_path = "~/.ele-agent/voice/vosk-model" }
tts = { engine = "auto", voice = "jarvis", speed = 1.0, volume = 1.0 }
vad = { engine = "silero", silence_timeout_ms = 500, min_speech_ms = 100 }

[memory]
short_term = { dynamic = true, max_turns = 50 }
long_term = { enabled = true, index_path = "~/.ele-agent/memory/faiss", embedding_model = "bge-small" }
episodic = { enabled = true, db_path = "~/.ele-agent/memory/episodic.db", retention = "forever", dedup = true }
project = { enabled = true, watch_paths = ["~/projects"], marker_files = ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git"] }

[plugins]
auto_update = true
allow_community = true
install_path = "~/.ele-agent/plugins"
marketplace_url = "https://api.ele-agent.dev/api/v1/plugins/marketplace"
templates = ["python", "json", "wasm"]

[security]
encryption = "age"
kdf = "hardware"                # hardware (TPM/Windows Hello), passphrase, keyfile
keyring_backend = "auto"        # auto, windows, macos, secret-service

[ui]
status_bar = ["connection", "model", "credits", "battery", "voice", "time"]
command_palette = "full"        # full, minimal
notifications = "sidebar_badge" # sidebar_badge, top_right, bottom_center
mouse_support = true
animations = true
animation_fps = 60
theme_preview = "pane"          # pane, instant, none
hidden_files_toggle = "ctrl+h"
editor_autosave = true
shell_pager = "builtin"
browser_stealth = true
diff_view = "both"              # side-by-side, unified, both
terminal_emulator = true
rag_reindex = "session_start"   # session_start, live, manual
session_export = "markdown"

[logging]
level = "INFO"                  # DEBUG, INFO, WARNING, ERROR
format = "json"                 # json, text
rotation = "daily"              # daily, weekly, size
retention_days = 30
per_module = true               # Enable per-module log levels

[advanced]
startup_timeout = 2             # seconds, target < 2s
hot_reload = true               # Watch config file for changes
lazy_load = true                # Lazy-load heavy components
accessibility = "full"          # full, basic, none
```

## Pydantic Model (Python)

```python
# backend/app/config.py
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Literal, Optional
import os

class LLMProviderConfig(BaseSettings):
    enabled: bool = True
    model: str
    priority: int = 5

class ToolsConfig(BaseSettings):
    file: dict = Field(default_factory=lambda: {"enabled": True, "confirm_write": True, "confirm_delete": True})
    shell: dict = Field(default_factory=lambda: {"enabled": True, "confirm_all": True, "timeout": 120})
    browser: dict = Field(default_factory=lambda: {"enabled": True, "headless": False, "stealth": True, "timeout": 30})
    app_launch: dict = Field(default_factory=lambda: {"enabled": True, "whitelist": ["code", "chrome", "firefox", "notepad", "explorer", "terminal"]})
    email: dict = Field(default_factory=lambda: {"enabled": False, "confirm_send": True})
    calendar: dict = Field(default_factory=lambda: {"enabled": False, "confirm_write": True})

class VoiceConfig(BaseSettings):
    wake_word: dict = Field(default_factory=lambda: {"enabled": True, "sensitivity": "medium", "keyword": "hey ellie"})
    stt: dict = Field(default_factory=lambda: {"engine": "auto", "whisper_model": "whisper-1", "vosk_path": "~/.ele-agent/voice/vosk-model"})
    tts: dict = Field(default_factory=lambda: {"engine": "auto", "voice": "jarvis", "speed": 1.0, "volume": 1.0})
    vad: dict = Field(default_factory=lambda: {"engine": "silero", "silence_timeout_ms": 500, "min_speech_ms": 100})

class MemoryConfig(BaseSettings):
    short_term: dict = Field(default_factory=lambda: {"dynamic": True, "max_turns": 50})
    long_term: dict = Field(default_factory=lambda: {"enabled": True, "index_path": "~/.ele-agent/memory/faiss", "embedding_model": "bge-small"})
    episodic: dict = Field(default_factory=lambda: {"enabled": True, "db_path": "~/.ele-agent/memory/episodic.db", "retention": "forever", "dedup": True})
    project: dict = Field(default_factory=lambda: {"enabled": True, "watch_paths": ["~/projects"], "marker_files": ["pyproject.toml", "package.json", "Cargo.toml", "go.mod", ".git"]})

class Settings(BaseSettings):
    # App
    APP_NAME: str = "ELE Agent"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Config file
    config_path: str = os.path.expanduser("~/.ele-agent/config.toml")
    
    # Database (SQLite for local)
    DATABASE_URL: str = "sqlite+aiosqlite:///~/.ele-agent/sessions.db"
    
    # Supabase (optional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Auth
    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Platform API Keys (from .env)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    NVIDIA_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Voice
    PORCUPINE_ACCESS_KEY: Optional[str] = None
    VOSK_MODEL_PATH: str = "~/.ele-agent/voice/vosk-model"
    
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
        extra = "allow"

settings = Settings()
```

## Config Loading Priority

1. **Defaults** (Pydantic model defaults)
2. **Config file** (`~/.ele-agent/config.toml`)
3. **Environment variables** (`.env` + shell)
4. **CLI flags** (highest priority)

## Hot Reload

```python
# Watch config file for changes
from watchfiles import watch

async def watch_config():
    async for changes in watch(settings.config_path):
        for change in changes:
            if change[0] == 1:  # Modified
                settings = load_config()  # Re-parse TOML
                apply_theme(settings.app.theme)
                # Notify UI components
```