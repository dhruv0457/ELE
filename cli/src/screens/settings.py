"""Settings Screen — API keys, model selection, preferences"""
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Static, Input, Button, Label, Select, Switch
from textual.binding import Binding

from ..store import store
from ..config import cli_config, save_cli_config
from .. import llm as engine


class SettingsScreen(Container):
    """Settings — minimal, focused."""

    DEFAULT_CSS = """
    SettingsScreen { display: none; padding: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("⚙  SETTINGS", classes="screen-header")

        with VerticalScroll():
            # ── API Keys ────────────────────────────────────────────
            yield Static("API KEYS", classes="settings-section-title")
            yield Static(
                "[dim]Keys are saved to [bold]~/.ele-agent/.env[/]. Never commit this file.[/]",
                classes="settings-hint"
            )

            for env_key, label, placeholder in [
                ("NVIDIA_API_KEY", "NVIDIA API Key", "nvapi-..."),
                ("OPENAI_API_KEY", "OpenAI API Key", "sk-..."),
                ("GEMINI_API_KEY", "Gemini API Key", "AIza..."),
                ("ANTHROPIC_API_KEY", "Anthropic API Key", "sk-ant-..."),
                ("GROQ_API_KEY", "Groq API Key", "gsk_..."),
            ]:
                current = engine._KEYS.get(env_key, "")
                masked = current[:4] + "••••" + current[-4:] if len(current) > 8 else ""
                with Horizontal(classes="settings-row"):
                    yield Label(f"[dim]{label}[/]", classes="settings-label")
                    yield Input(
                        value=masked,
                        placeholder=placeholder,
                        password=True,
                        id=f"key_{env_key}",
                        classes="settings-input"
                    )

            yield Button("💾  Save API Keys", id="save_keys_btn", classes="save-btn")

            yield Static(" ", classes="settings-spacer")

            # ── Model selection ─────────────────────────────────────
            yield Static("DEFAULT MODEL", classes="settings-section-title")
            with Horizontal(classes="settings-row"):
                yield Label("[dim]Provider / Model[/]", classes="settings-label")
                yield Select(
                    [
                        ("Auto (best available)", "auto"),
                        ("NVIDIA — Llama 3.3 70B", "nvidia/meta/llama-3.3-70b-instruct"),
                        ("NVIDIA — Nemotron 70B", "nvidia/nvidia/llama-3.1-nemotron-70b-instruct"),
                        ("NVIDIA — DeepSeek R1", "nvidia/deepseek-ai/deepseek-r1"),
                        ("Gemini — 2.0 Flash", "gemini/gemini-2.0-flash-exp"),
                        ("Gemini — 1.5 Pro", "gemini/gemini-1.5-pro"),
                        ("OpenAI — GPT-4o", "openai/gpt-4o"),
                        ("OpenAI — GPT-4o Mini", "openai/gpt-4o-mini"),
                        ("Anthropic — Claude 3.5 Sonnet", "anthropic/claude-3-5-sonnet-20241022"),
                        ("Anthropic — Claude 3 Haiku", "anthropic/claude-3-haiku-20240307"),
                        ("Groq — Llama 3.3 70B", "groq/llama-3.3-70b-versatile"),
                        ("Ollama — Llama 3 (local)", "ollama/llama3"),
                    ],
                    prompt="Select model",
                    id="model_select",
                    classes="settings-select"
                )

            yield Static(" ", classes="settings-spacer")

            # ── Appearance ──────────────────────────────────────────
            yield Static("APPEARANCE", classes="settings-section-title")
            with Horizontal(classes="settings-row"):
                yield Label("[dim]Theme[/]", classes="settings-label")
                yield Select(
                    [
                        ("Tokyo Night (default)", "tokyo-night"),
                        ("Catppuccin Mocha", "catppuccin"),
                        ("Dracula", "dracula"),
                        ("Gruvbox Dark", "gruvbox"),
                        ("Nord", "nord"),
                        ("One Dark", "one-dark"),
                        ("Monokai", "monokai"),
                    ],
                    prompt="Select theme",
                    id="theme_select",
                    classes="settings-select"
                )

            yield Static(" ", classes="settings-spacer")

            # ── Backend ─────────────────────────────────────────────
            yield Static("BACKEND (Optional)", classes="settings-section-title")
            yield Static(
                "[dim]The backend enables browser automation, desktop control, and persistent memory.\n"
                "Chat works without it using direct API calls.[/]",
                classes="settings-hint"
            )
            with Horizontal(classes="settings-row"):
                yield Label("[dim]Auto-start backend[/]", classes="settings-label")
                yield Switch(value=cli_config.auto_start_backend, id="auto_backend_switch")

            with Horizontal(classes="settings-row"):
                yield Label("[dim]Backend port[/]", classes="settings-label")
                yield Input(
                    value=str(cli_config.backend_port),
                    placeholder="8000",
                    id="backend_port_input",
                    classes="settings-input-sm"
                )

            yield Static(" ", classes="settings-spacer")
            with Horizontal():
                yield Button("💾  Save Settings", id="save_settings_btn", classes="save-btn")
                yield Button("🔄  Test Connection", id="test_conn_btn", classes="test-btn")

    def on_mount(self) -> None:
        engine.reload_keys()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_keys_btn":
            await self._save_keys()
        elif event.button.id == "save_settings_btn":
            self._save_settings()
        elif event.button.id == "test_conn_btn":
            await self._test_connection()

    async def _save_keys(self) -> None:
        """Write API keys to ~/.ele-agent/.env"""
        env_path = Path.home() / ".ele-agent" / ".env"
        if not env_path.parent.exists():
            env_path.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if env_path.exists():
            for line in env_path.read_text("utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    existing[k.strip()] = v.strip()

        key_fields = [
            ("NVIDIA_API_KEY", "key_NVIDIA_API_KEY"),
            ("OPENAI_API_KEY", "key_OPENAI_API_KEY"),
            ("GEMINI_API_KEY", "key_GEMINI_API_KEY"),
            ("ANTHROPIC_API_KEY", "key_ANTHROPIC_API_KEY"),
            ("GROQ_API_KEY", "key_GROQ_API_KEY"),
        ]

        updated = 0
        for env_key, widget_id in key_fields:
            try:
                inp = self.query_one(f"#{widget_id}", Input)
                val = inp.value.strip()
                if val and "••••" not in val and len(val) > 4:
                    existing[env_key] = val
                    updated += 1
            except Exception:
                pass

        lines = [f"{k}={v}" for k, v in existing.items()]
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        engine.reload_keys()
        self.app.notify(f"✅ Saved {updated} API key(s) to ~/.ele-agent/.env")

    def _save_settings(self) -> None:
        try:
            # Theme
            try:
                theme_sel = self.query_one("#theme_select", Select)
                if theme_sel.value and theme_sel.value != Select.BLANK:
                    cli_config.theme = str(theme_sel.value)
                    self.app.apply_theme(cli_config.theme)
            except Exception:
                pass

            # Model
            try:
                model_sel = self.query_one("#model_select", Select)
                if model_sel.value and model_sel.value != Select.BLANK:
                    val = str(model_sel.value)
                    if val == "auto":
                        store.set_active_model("auto", "auto")
                    elif "/" in val:
                        provider, model = val.split("/", 1)
                        store.set_active_model(model, provider)
            except Exception:
                pass

            # Backend port
            try:
                port_inp = self.query_one("#backend_port_input", Input)
                cli_config.backend_port = int(port_inp.value or "8000")
            except Exception:
                pass

            # Auto-start
            try:
                sw = self.query_one("#auto_backend_switch", Switch)
                cli_config.auto_start_backend = sw.value
            except Exception:
                pass

            save_cli_config(cli_config)
            self.app.notify("✅ Settings saved")
        except Exception as e:
            self.app.notify(f"⚠ Save failed: {e}", severity="error")

    async def _test_connection(self) -> None:
        self.app.notify("Testing LLM connection...")
        try:
            engine.reload_keys()
            provider, model = engine.get_best_provider()
            if provider == "none":
                self.app.notify("⚠ Please enter and save an API key first", severity="warning")
                return

            msgs = [{"role": "user", "content": "Say 'OK' only."}]
            result = ""
            error_found = None
            async for event in engine.stream_response(msgs, provider, model):
                if event.type == "delta":
                    result += event.content
                elif event.type == "error":
                    error_found = event.content
                    break
                elif event.type == "final":
                    break

            if error_found:
                self.app.notify(f"❌ {error_found[:60]}", severity="error")
            elif result:
                self.app.notify(f"✅ {provider.upper()} connected! ({result[:20].strip()})")
            else:
                self.app.notify("⚠ No response from LLM", severity="warning")
        except Exception as e:
            self.app.notify(f"❌ Connection failed: {e}", severity="error")