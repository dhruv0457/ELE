"""Settings Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, Select, Switch, Collapsible
from textual import events

from ..config import cli_config, save_cli_config


class SettingsScreen(Container):
    """Settings Screen"""

    DEFAULT_CSS = """
    SettingsScreen {
        layout: vertical;
        padding: 2;
        display: none;
    }

    SettingsScreen.visible {
        display: block;
    }

    .setting-group {
        margin: 1 0;
        padding: 1;
        border: solid $primary;
    }

    .setting-label {
        text-style: bold;
        margin-bottom: 1;
    }

    .setting-item {
        margin: 1 0;
    }
    """

    def compose(self):
        yield Static("⚙ Settings", classes="setting-label")

        with Collapsible(title="🎨 Appearance", collapsed=False):
            yield Select(
                [("Tokyo Night", "tokyo-night"), ("Catppuccin", "catppuccin"),
                 ("Dracula", "dracula"), ("Gruvbox", "gruvbox"),
                 ("Nord", "nord"), ("Solarized", "solarized"),
                 ("One Dark", "one-dark"), ("Monokai", "monokai"),
                 ("GitHub Dark", "github-dark")],
                value=cli_config.theme,
                id="theme_select",
            )

        with Collapsible(title="🔗 Backend", collapsed=False):
            yield Input(value=str(cli_config.backend_port), placeholder="Port", id="backend_port")
            yield Switch(value=cli_config.auto_start_backend, id="auto_start_backend")
            yield Label("Auto-start backend on launch")

        with Collapsible(title="🤖 LLM", collapsed=False):
            yield Select(
                [("Auto", "auto"), ("Gemini", "gemini"), ("Groq", "groq"),
                 ("NVIDIA", "nvidia"), ("Claude", "claude"), ("GPT", "openai")],
                value=cli_config.default_model,
                id="default_model",
            )

        with Collapsible(title="🔧 Tools", collapsed=False):
            yield Switch(value=cli_config.file_enabled, id="file_enabled")
            yield Label("File operations")
            yield Switch(value=cli_config.shell_enabled, id="shell_enabled")
            yield Label("Shell commands")
            yield Switch(value=cli_config.browser_enabled, id="browser_enabled")
            yield Label("Browser automation")

        with Collapsible(title="🎤 Voice", collapsed=False):
            yield Switch(value=cli_config.wake_word_enabled, id="wake_word_enabled")
            yield Label("Wake word (Hey Ellie)")
            yield Select(
                [("Auto", "auto"), ("Whisper API", "whisper"), ("Vosk (offline)", "vosk")],
                value=cli_config.stt_engine,
                id="stt_engine",
            )
            yield Select(
                [("Auto", "auto"), ("Edge-TTS", "edge"), ("Coqui (offline)", "coqui"), ("System", "pyttsx3")],
                value=cli_config.tts_engine,
                id="tts_engine",
            )

        with Collapsible(title="💾 Save", collapsed=False):
            yield Button("Save Settings", id="save_btn", variant="primary")
            yield Button("Reset to Defaults", id="reset_btn", variant="warning")

    async def on_select_changed(self, event: Select.Changed):
        if event.select.id == "theme_select":
            cli_config.theme = event.value
            self.app.apply_theme(event.value)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save_btn":
            await self.save_settings()
        elif event.button.id == "reset_btn":
            await self.reset_settings()

    async def save_settings(self):
        """Save all settings"""
        # Update config from UI
        cli_config.theme = self.query_one("#theme_select").value
        cli_config.backend_port = int(self.query_one("#backend_port").value or 8000)
        cli_config.auto_start_backend = self.query_one("#auto_start_backend").value
        cli_config.default_model = self.query_one("#default_model").value
        cli_config.file_enabled = self.query_one("#file_enabled").value
        cli_config.shell_enabled = self.query_one("#shell_enabled").value
        cli_config.browser_enabled = self.query_one("#browser_enabled").value
        cli_config.wake_word_enabled = self.query_one("#wake_word_enabled").value
        cli_config.stt_engine = self.query_one("#stt_engine").value
        cli_config.tts_engine = self.query_one("#tts_engine").value

        save_cli_config(cli_config)
        self.app.apply_theme(cli_config.theme)
        self.notify("Settings saved!", title="Success")

    async def reset_settings(self):
        """Reset to defaults"""
        from ..config import CLIConfig
        new_config = CLIConfig()
        # Update UI
        self.query_one("#theme_select").value = new_config.theme
        self.query_one("#backend_port").value = str(new_config.backend_port)
        self.query_one("#auto_start_backend").value = new_config.auto_start_backend
        self.query_one("#default_model").value = new_config.default_model
        self.query_one("#file_enabled").value = new_config.file_enabled
        self.query_one("#shell_enabled").value = new_config.shell_enabled
        self.query_one("#browser_enabled").value = new_config.browser_enabled
        self.query_one("#wake_word_enabled").value = new_config.wake_word_enabled
        self.query_one("#stt_engine").value = new_config.stt_engine
        self.query_one("#tts_engine").value = new_config.tts_engine

        self.notify("Settings reset to defaults", title="Reset")