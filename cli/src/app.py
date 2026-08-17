"""Main CLI Application"""
import asyncio
import os
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Label
from textual.screen import Screen
from textual import events

from .store import store, ViewMode, OverlayStatus
from .screens.chat import ChatScreen
from .screens.autonomous import AutonomousScreen
from .screens.settings import SettingsScreen
from .screens.plugins import PluginsScreen
from .screens.tools import ToolsScreen
from .widgets.ellie_avatar import EllieAvatar
from .widgets.status_bar import StatusBar
from .config import cli_config


class ELEApp(App):
    """Main ELE Agent CLI Application"""

    CSS_PATH = "app.tcss"
    TITLE = "ELE Agent"

    BINDINGS = [
        Binding("space", "leader_mode", "Leader", show=False),
        Binding("space,e", "toggle_mode", "Toggle Ellie"),
        Binding("space,v", "toggle_voice", "Voice"),
        Binding("space,q", "quit_mode", "Quit Mode"),
        Binding("space,h", "command_palette", "Commands"),
        Binding("space,s", "save_session", "Save"),
        Binding("space,n", "new_session", "New Session"),
        Binding("space,t", "theme_selector", "Theme"),
        Binding("space,p", "plugin_manager", "Plugins"),
        Binding("space,/", "search_messages", "Search"),
        Binding("space,?", "shell_history", "Shell History"),
        Binding("escape", "exit_mode", "Exit Mode"),
        Binding("ctrl+h", "toggle_hidden", "Hidden Files"),
        Binding("ctrl+d", "half_page_down", "Page Down"),
        Binding("ctrl+u", "half_page_up", "Page Up"),
    ]

    def __init__(self):
        super().__init__()
        self.leader_mode = False
        self.leader_timeout = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            ChatScreen(id="chat_screen"),
            AutonomousScreen(id="autonomous_screen"),
            SettingsScreen(id="settings_screen"),
            PluginsScreen(id="plugins_screen"),
            ToolsScreen(id="tools_screen"),
            id="main_container",
        )
        yield EllieAvatar(id="ellie_avatar")
        yield StatusBar(id="status_bar")
        yield Footer()

    def on_mount(self) -> None:
        # Apply theme
        self.apply_theme(cli_config.theme)

        # Start backend auto-start
        if cli_config.auto_start_backend:
            self.run_worker(self.start_backend(), exclusive=True)

        # Watch for config changes
        self.run_worker(self.watch_config(), exclusive=True)

    def apply_theme(self, theme_name: str):
        """Apply a theme"""
        theme_map = {
            "tokyo-night": "tokyo-night",
            "catppuccin": "catppuccin-mocha",
            "dracula": "dracula",
            "gruvbox": "gruvbox",
            "nord": "nord",
            "solarized": "solarized-dark",
            "one-dark": "atom-one-dark",
            "monokai": "monokai",
            "github-dark": "flexoki",
        }
        textual_theme = theme_map.get(theme_name, "tokyo-night")
        try:
            self.theme = textual_theme
        except Exception as e:
            # Fallback if the theme is unavailable
            self.theme = "tokyo-night"

    async def start_backend(self):
        """Start backend subprocess if not already running."""
        import sys
        import shutil
        from . import backend as be

        # If backend is already up, nothing to do
        if be.is_backend_up():
            store.set_backend_status(True, "connected")
            return

        # Find a python that can run uvicorn. Prefer this interpreter, then
        # common venv/conda locations.
        candidates = [sys.executable, shutil.which("python") or "python"]
        # Add the known conda env on this machine if present
        conda_py = r"E:\ANACONDA\envs\ele-agent\python.exe"
        if os.name == "nt" and os.path.exists(conda_py):
            if conda_py not in candidates:
                candidates.append(conda_py)

        backend_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "backend")
        )

        for py in candidates:
            try:
                proc = await asyncio.create_subprocess_exec(
                    py, "-m", "uvicorn", "app.main:app",
                    "--host", "localhost",
                    "--port", "8000",
                    cwd=backend_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                # Wait a bit for startup
                await asyncio.sleep(3)
                proc.kill()
                if be.is_backend_up():
                    store.set_backend_status(True, "connected")
                    return
            except Exception:
                continue

        store.set_backend_status(False, "not running")

    async def watch_config(self):
        """Watch config file for changes"""
        import watchfiles
        config_path = os.path.expanduser("~/.ele-agent/config.toml")
        # Ensure the file exists so watchfiles has something to watch
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            if not os.path.exists(config_path):
                # Save current config to seed the file
                from .config import save_cli_config
                save_cli_config(cli_config)
        except Exception:
            pass

        try:
            async for _ in watchfiles.awatch(config_path):
                # Reload config
                from .config import load_cli_config, cli_config as config
                new_config = load_cli_config()
                # Update theme if changed
                if new_config.theme != config.theme:
                    config.theme = new_config.theme
                    self.apply_theme(new_config.theme)
        except FileNotFoundError:
            # Config file was deleted; nothing to watch
            pass

    # Actions
    def action_leader_mode(self):
        """Enter leader mode (Vim-style Space leader)"""
        self.leader_mode = True
        if self.leader_timeout:
            self.leader_timeout.cancel()
        self.leader_timeout = self.set_timer(1.0, self._exit_leader_mode)

    def _exit_leader_mode(self):
        self.leader_mode = False

    def action_toggle_mode(self):
        """Toggle between Chat and Autonomous mode"""
        if store.mode == "chat":
            store.mode = "autonomous"
            self.query_one("#chat_screen").display = False
            self.query_one("#autonomous_screen").display = True
            self.query_one("#autonomous_screen").focus()
            # Start autonomous mode
            autonomous = self.query_one("#autonomous_screen")
            autonomous.start_voice_pipeline()
        else:
            store.mode = "chat"
            self.query_one("#autonomous_screen").display = False
            self.query_one("#chat_screen").display = True
            self.query_one("#chat_screen").focus()
            # Stop autonomous mode
            autonomous = self.query_one("#autonomous_screen")
            autonomous.stop_voice_pipeline()

    def action_quit_mode(self):
        """Quit current mode (exit autonomous)"""
        if store.mode == "autonomous":
            self.action_toggle_mode()

    def action_toggle_voice(self):
        """Toggle voice listening"""
        store.voice_listening = not store.voice_listening
        store.voice_enabled = store.voice_listening

    def action_command_palette(self):
        """Show command palette"""
        self.notify("Command palette not yet implemented", title="Commands")

    def action_save_session(self):
        """Save current session"""
        self.notify("Session saved", title="Saved")

    def action_new_session(self):
        """Create new session"""
        store.create_session()
        self.notify("New session created", title="New Session")

    def action_theme_selector(self):
        """Show theme selector"""
        self.notify("Theme selector not yet implemented", title="Themes")

    def action_plugin_manager(self):
        """Switch to plugins screen"""
        self.switch_screen("plugins")

    def action_search_messages(self):
        """Search messages"""
        self.notify("Search not yet implemented", title="Search")

    def action_shell_history(self):
        """Show shell history"""
        self.notify("Shell history not yet implemented", title="History")

    def action_exit_mode(self):
        """Exit current mode (Escape)"""
        if self.leader_mode:
            self._exit_leader_mode()
        elif store.mode == "autonomous":
            self.action_toggle_mode()

    def action_toggle_hidden(self):
        """Toggle hidden files"""
        self.notify("Toggle hidden files", title="Files")

    def action_half_page_down(self):
        """Half page down"""
        pass

    def action_half_page_up(self):
        """Half page up"""
        pass

    def switch_screen(self, screen_name: str):
        """Switch to a specific screen"""
        screens = {
            "chat": "#chat_screen",
            "autonomous": "#autonomous_screen",
            "settings": "#settings_screen",
            "plugins": "#plugins_screen",
            "tools": "#tools_screen",
        }
        for name, selector in screens.items():
            screen = self.query_one(selector)
            screen.display = (name == screen_name)
            if name == screen_name:
                screen.focus()


def main():
    """Entry point for the CLI."""
    app = ELEApp()
    app.run()


if __name__ == "__main__":
    main()