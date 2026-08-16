"""CLI Configuration"""
import os
import tomli
import tomli_w
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field


class CLIConfig(BaseModel):
    """CLI-specific configuration"""

    # App
    theme: str = "tokyo-night"
    language: str = "en"
    auto_update: bool = True
    start_minimized: bool = False
    telemetry: str = "errors"

    # Backend connection
    backend_host: str = "localhost"
    backend_port: int = 8000
    ws_path: str = "/api/v1/ws/chat"
    auto_start_backend: bool = True

    # LLM
    default_model: str = "auto"
    max_parallel: int = 4
    timeout_seconds: int = 60

    # Tools
    file_enabled: bool = True
    shell_enabled: bool = True
    browser_enabled: bool = True
    app_launch_enabled: bool = True

    # Voice
    wake_word_enabled: bool = True
    wake_word_sensitivity: str = "medium"
    stt_engine: str = "auto"
    tts_voice: str = "jarvis"
    tts_engine: str = "auto"
    voice_speed: float = 1.0
    volume: float = 1.0

    # UI
    animation_fps: int = 60
    show_token_cost: bool = True
    sidebar_collapsed: bool = False

    class Config:
        extra = "allow"


# Global config instance
cli_config = CLIConfig()


def get_config_path() -> Path:
    """Get CLI config file path"""
    if os.name == "nt":
        return Path(os.environ.get("USERPROFILE", "~")) / ".ele-agent" / "config.toml"
    return Path.home() / ".ele-agent" / "config.toml"


def load_cli_config() -> CLIConfig:
    """Load CLI config from TOML file"""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "rb") as f:
                data = tomli.load(f)
            # Extract CLI section
            cli_data = data.get("cli", {})
            return CLIConfig(**cli_data)
        except Exception:
            pass
    return CLIConfig()


def save_cli_config(config: CLIConfig):
    """Save CLI config to TOML file"""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing full config
    full_data = {}
    if config_path.exists():
        with open(config_path, "rb") as f:
            full_data = tomli.load(f)

    # Update CLI section
    full_data["cli"] = config.model_dump(exclude_none=True)

    with open(config_path, "wb") as f:
        tomli_w.dump(full_data, f)


# Load on import
cli_config = load_cli_config()