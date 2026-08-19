"""CLI Configuration"""
import os
import tomllib
from pathlib import Path
from typing import Any, Dict
try:
    import tomli as _tomli
    _tomli_write = None
    try:
        import tomli_w as _tomli_write
    except ImportError:
        pass
except ImportError:
    _tomli = None
    _tomli_write = None


class CLIConfig:
    """CLI-specific configuration with sensible defaults."""

    def __init__(self):
        # App
        self.theme: str = "tokyo-night"
        self.language: str = "en"
        self.auto_update: bool = True
        self.telemetry: str = "errors"

        # Backend connection (optional — chat works without it)
        self.backend_host: str = "localhost"
        self.backend_port: int = 8000
        self.auto_start_backend: bool = False  # off by default for speed

        # LLM
        self.default_provider: str = "auto"
        self.default_model: str = "auto"
        self.timeout_seconds: int = 120

        # Tools
        self.file_enabled: bool = True
        self.shell_enabled: bool = True
        self.browser_enabled: bool = True

        # Voice
        self.voice_enabled: bool = False
        self.wake_word: str = "hey ellie"
        self.tts_engine: str = "auto"

        # UI
        self.show_token_cost: bool = True


# Global config instance
cli_config = CLIConfig()


def get_config_path() -> Path:
    base = Path(os.environ.get("USERPROFILE", "~")) if os.name == "nt" else Path.home()
    return base / ".ele-agent" / "config.toml"


def load_cli_config() -> CLIConfig:
    config = CLIConfig()
    config_path = get_config_path()

    if config_path.exists():
        try:
            data: Dict[str, Any] = {}
            raw = config_path.read_bytes()

            # Try stdlib tomllib (Python 3.11+) first
            try:
                data = tomllib.loads(raw.decode("utf-8"))
            except Exception:
                if _tomli:
                    import io
                    data = _tomli.load(io.BytesIO(raw))

            cli_data = data.get("cli", data)
            for key, val in cli_data.items():
                if hasattr(config, key):
                    setattr(config, key, val)
        except Exception:
            pass

    return config


def save_cli_config(config: CLIConfig) -> None:
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    data = {k: v for k, v in config.__dict__.items() if not k.startswith("_")}
    content = "\n".join(f'{k} = {_toml_val(v)}' for k, v in data.items())

    if _tomli_write:
        with open(config_path, "wb") as f:
            _tomli_write.dump({"cli": data}, f)
    else:
        config_path.write_text(f"[cli]\n{content}\n", encoding="utf-8")


def _toml_val(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return f'"{v}"'
    return str(v)


# Load on import
cli_config = load_cli_config()