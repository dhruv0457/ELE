"""ELE Agent — Main App & TCSS"""
import os
import sys
import asyncio
import shutil
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer
from textual.binding import Binding

from .store import store, ViewMode
from .screens.chat import ChatScreen
from .screens.automate import AutomateScreen
from .screens.settings import SettingsScreen
from .screens.tools import ToolsScreen
from .config import cli_config


class ELEApp(App):
    """ELE — Instant-boot AI terminal agent."""

    TITLE = "ELE Agent"
    CSS = """
/* ══════════════════════════════════════════════════
   GLOBAL
══════════════════════════════════════════════════ */
Screen {
    background: #080C14;
    color: #CBD5E1;
}

Header {
    background: #080C14;
    color: #00FFE0;
    height: 1;
    dock: top;
}

Footer {
    background: #080C14;
    color: #475569;
    height: 1;
    dock: bottom;
}

Footer > .footer--highlight { background: #080C14; color: #00FFE0; }
Footer > .footer--highlight-key { background: #080C14; color: #A855F7; text-style: bold; }
Footer > .footer--key { color: #A855F7; text-style: bold; }

/* ══════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════ */
Button {
    background: transparent;
    color: #94A3B8;
    border: none;
    height: 1;
    min-width: 3;
}
Button:hover {
    background: #0F172A;
    color: #00FFE0;
}
Button.-primary, Button.save-btn {
    background: #00FFE0;
    color: #080C14;
    text-style: bold;
}
Button.run-btn {
    background: #00FF9D22;
    color: #00FF9D;
    border: solid #00FF9D44;
    height: 1;
}
Button.run-btn:hover { background: #00FF9D44; }
Button.stop-btn { color: #FF3366; }
Button.clear-btn { color: #475569; }
Button.icon-btn { width: 3; height: 1; padding: 0; color: #475569; }
Button.icon-btn:hover { color: #00FFE0; }
Button.test-btn { background: transparent; color: #A855F7; border: solid #A855F744; }

/* ══════════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════════ */
Input, TextArea {
    background: #0D1117;
    border: tall #1E293B;
    color: #CBD5E1;
}
Input:focus, TextArea:focus {
    border: tall #00FFE0;
    background: #0D1117;
}
Select {
    background: #0D1117;
    border: tall #1E293B;
    color: #CBD5E1;
}
Select:focus { border: tall #00FFE0; }

/* ══════════════════════════════════════════════════
   LISTVIEW
══════════════════════════════════════════════════ */
ListView {
    background: transparent;
    border: none;
    height: 1fr;
}
ListItem {
    background: transparent;
    color: #CBD5E1;
    padding: 0;
}
ListItem:hover { background: #0F172A; }
ListItem.-highlight { background: #0F172A; color: #00FFE0; }

/* ══════════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════════ */
Scrollbar { background: #080C14; }
Scrollbar > .scrollbar--slider { background: #1E293B; }
Scrollbar > .scrollbar--slider:hover { background: #00FFE0; }

/* ══════════════════════════════════════════════════
   MARKDOWN
══════════════════════════════════════════════════ */
Markdown { background: transparent; color: #CBD5E1; }
MarkdownFence { background: #0D1117; border: solid #1E293B; padding: 1; color: #38BDF8; }
MarkdownBlockQuote { border-left: wide #A855F7; padding-left: 1; background: #0F172A; }
MarkdownH1, MarkdownH2, MarkdownH3 { color: #00FFE0; text-style: bold; }
MarkdownBullet { color: #A855F7; }

/* ══════════════════════════════════════════════════
   MAIN CONTAINER
══════════════════════════════════════════════════ */
#main_stack {
    layout: horizontal;
    width: 100%;
    height: 100%;
}

/* ══════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════ */
#sidebar {
    width: 20;
    background: #0A0F1C;
    border-right: solid #1E293B;
    padding: 0 1;
    height: 100%;
}

#sidebar_logo {
    color: #00FFE0;
    text-style: bold;
    padding: 1 0;
    height: 3;
    content-align: center middle;
}

.sidebar-divider { color: #1E293B; height: 1; }
.sidebar-section-title { color: #475569; height: 1; text-style: bold; margin-top: 1; }

.nav-item {
    background: transparent;
    color: #64748B;
    height: 2;
    width: 1fr;
    border: none;
    content-align: left middle;
    padding: 0 1;
}
.nav-item:hover {
    background: #0F172A;
    color: #CBD5E1;
}
.nav-item.active {
    color: #00FFE0;
    background: #0F172A;
    border-left: wide #00FFE0;
}

#session_list {
    height: 1fr;
    background: transparent;
}

.new-session-btn {
    height: 1;
    width: 1fr;
    color: #A855F7;
    background: transparent;
    border: none;
    margin-top: 1;
}
.new-session-btn:hover { color: #00FFE0; background: #0F172A; }

/* ══════════════════════════════════════════════════
   CHAT SCREEN
══════════════════════════════════════════════════ */
#chat_layout { layout: horizontal; height: 100%; width: 1fr; }
#chat_main { layout: vertical; height: 100%; width: 1fr; }

#chat_status_bar {
    height: 1;
    background: #0A0F1C;
    border-bottom: solid #1E293B;
    padding: 0 1;
    color: #64748B;
}

#messages_list {
    height: 1fr;
    width: 100%;
    background: #080C14;
    border: none;
    padding: 0 1;
}

.thinking-panel {
    background: #0F0A1E;
    border-left: wide #A855F7;
    border-bottom: solid #1E293B;
    padding: 0 1;
    height: auto;
    min-height: 1;
    max-height: 4;
    color: #A855F7;
}
.thinking-panel.hidden { display: none; }

#input_bar {
    background: #0A0F1C;
    border-top: solid #1E293B;
    padding: 1;
    height: auto;
    min-height: 5;
    max-height: 8;
}

#input_area {
    background: #0D1117;
    border: tall #1E293B;
    height: 3;
    max-height: 6;
    width: 1fr;
    color: #CBD5E1;
}
#input_area:focus { border: tall #00FFE0; }

#input_buttons { width: 5; padding-left: 1; }
.send-btn {
    background: #00FFE0;
    color: #080C14;
    text-style: bold;
    height: 3;
    width: 5;
    border: none;
}
.send-btn:hover { background: #00FF9D; }
.voice-btn {
    background: transparent;
    color: #475569;
    height: 1;
    width: 5;
    border: none;
    margin-top: 1;
}
.voice-btn:hover { color: #00FFE0; }

/* ══════════════════════════════════════════════════
   MESSAGE BUBBLES
══════════════════════════════════════════════════ */
MessageBubble { width: 1fr; margin: 0 0 1 0; padding: 0; }
MessageBubble .bubble-content { padding: 0; }

/* ══════════════════════════════════════════════════
   AUTOMATE SCREEN
══════════════════════════════════════════════════ */
#automate_header, #automate_sub {
    padding: 0 1;
    height: 1;
}

#automate_layout { height: 1fr; layout: horizontal; }

#log_panel {
    width: 1fr;
    background: #080C14;
    border-right: solid #1E293B;
    padding: 0 1;
}

#task_panel {
    width: 1fr;
    padding: 0 1;
}

#task_input {
    height: 6;
    border: tall #1E293B;
    background: #0D1117;
    margin-bottom: 1;
}
#task_input:focus { border: tall #00FFE0; }

#task_controls { height: 1; margin-bottom: 1; }

.task-result {
    height: 1fr;
    background: #0D1117;
    border: solid #1E293B;
    padding: 1;
    overflow-y: auto;
}

/* ══════════════════════════════════════════════════
   SETTINGS SCREEN
══════════════════════════════════════════════════ */
SettingsScreen { padding: 0 1; }

.settings-section-title {
    color: #00FFE0;
    text-style: bold;
    height: 2;
    margin-top: 1;
}

.settings-hint {
    color: #475569;
    height: auto;
    margin-bottom: 1;
}

.settings-spacer { height: 1; }

.settings-row {
    height: 3;
    layout: horizontal;
    margin-bottom: 1;
}

.settings-label {
    width: 24;
    height: 3;
    content-align: left middle;
    color: #94A3B8;
}

.settings-input {
    width: 1fr;
    height: 3;
    background: #0D1117;
}

.settings-input-sm {
    width: 12;
    height: 3;
    background: #0D1117;
}

.settings-select {
    width: 1fr;
    height: 3;
    background: #0D1117;
}

/* ══════════════════════════════════════════════════
   TOOLS SCREEN
══════════════════════════════════════════════════ */
#tools_body { layout: horizontal; height: 1fr; }

#tools_nav {
    width: 18;
    background: #0A0F1C;
    border-right: solid #1E293B;
    padding: 1;
}

.tool-nav-btn {
    height: 2;
    width: 1fr;
    background: transparent;
    color: #64748B;
    border: none;
    content-align: left middle;
    margin-bottom: 1;
}
.tool-nav-btn:hover { color: #CBD5E1; background: #0F172A; }
.tool-nav-btn.active-tab {
    color: #00FFE0;
    background: #0F172A;
    border-left: wide #00FFE0;
}

#tools_content { width: 1fr; height: 100%; }

.tool-panel { height: 100%; padding: 1; }
.tool-panel.hidden { display: none; }
.tool-panel-title { color: #00FFE0; text-style: bold; height: 1; margin-bottom: 1; }
.tool-panel-header { height: 3; layout: horizontal; margin-bottom: 1; }

.path-label { color: #475569; height: 1; margin-bottom: 1; }

#file_tree { height: 1fr; background: #0D1117; border: solid #1E293B; }

#shell_output { height: 1fr; background: #0D1117; border: solid #1E293B; margin-bottom: 1; padding: 1; }

#shell_input_row { height: 3; layout: horizontal; }
.shell-prompt { width: 3; height: 3; content-align: left middle; color: #00FF9D; }

.browser-hint { color: #475569; height: auto; margin-bottom: 1; }
#browser_status { color: #00FF9D; height: 1; }

#desktop_log { height: 1fr; background: #0D1117; border: solid #1E293B; margin-top: 1; padding: 1; }

/* ══════════════════════════════════════════════════
   SHARED SCREEN ELEMENTS
══════════════════════════════════════════════════ */
.screen-header {
    color: #00FFE0;
    text-style: bold;
    height: 2;
    padding: 0 1;
    border-bottom: solid #1E293B;
}

.panel-title {
    color: #475569;
    text-style: bold;
    height: 1;
    margin-bottom: 1;
}

/* Tree */
Tree { background: #0D1117; color: #CBD5E1; }
Tree:focus { border: none; }
Tree > .tree--cursor { background: #0F172A; color: #00FFE0; }
Tree > .tree--guides { color: #1E293B; }

/* Switch */
Switch { background: #1E293B; }
Switch > .switch--slider { background: #475569; }
Switch.-on { background: #00FF9D44; }
Switch.-on > .switch--slider { background: #00FF9D; }

/* Notification / Toast */
Toast { background: #0F172A; color: #00FF9D; border: solid #00FFE044; }
"""

    BINDINGS = [
        Binding("ctrl+c", "quit_app", "Quit", priority=True),
        Binding("ctrl+q", "quit_app", "Quit"),
        Binding("ctrl+1", "go_chat", "Chat"),
        Binding("ctrl+2", "go_automate", "Automate"),
        Binding("ctrl+3", "go_tools", "Tools"),
        Binding("ctrl+4", "go_settings", "Settings"),
        Binding("ctrl+n", "new_session", "New Session"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_stack"):
            yield ChatScreen(id="screen_chat")
            yield AutomateScreen(id="screen_automate")
            yield ToolsScreen(id="screen_tools")
            yield SettingsScreen(id="screen_settings")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_theme(cli_config.theme)
        self._show_screen("chat")

        # Non-blocking: start backend silently in background
        if cli_config.auto_start_backend:
            self.run_worker(self._bg_backend_start(), exclusive=False)

    def _apply_theme(self, theme_name: str) -> None:
        theme_map = {
            "tokyo-night": "tokyo-night",
            "catppuccin": "catppuccin-mocha",
            "dracula": "dracula",
            "gruvbox": "gruvbox",
            "nord": "nord",
            "one-dark": "atom-one-dark",
            "monokai": "monokai",
            "solarized": "solarized-dark",
        }
        try:
            self.theme = theme_map.get(theme_name, "tokyo-night")
        except Exception:
            pass

    # Expose for settings screen
    def apply_theme(self, theme_name: str) -> None:
        self._apply_theme(theme_name)

    async def _bg_backend_start(self) -> None:
        """Non-blocking backend start — TUI is live before this completes."""
        from . import llm as engine

        # Quick check first
        if await engine.check_backend():
            store.set_backend_status(True, "connected")
            return

        backend_dir = Path(__file__).parents[2] / "backend"
        if not backend_dir.exists():
            return

        # Try to start backend
        proc = await engine.launch_backend_async(str(backend_dir), cli_config.backend_port)
        if not proc:
            return

        # Poll up to 8 attempts × 0.5s = 4s
        for _ in range(8):
            await asyncio.sleep(0.5)
            if await engine.check_backend():
                store.set_backend_status(True, "connected")
                try:
                    # Notify the chat screen to refresh status bar
                    chat = self.query_one("#screen_chat", ChatScreen)
                    chat._update_status_bar()
                except Exception:
                    pass
                return

    def _show_screen(self, name: str) -> None:
        """Hide all screens, show the target."""
        screens = {
            "chat": "#screen_chat",
            "automate": "#screen_automate",
            "tools": "#screen_tools",
            "settings": "#screen_settings",
        }
        for sid in screens.values():
            try:
                self.query_one(sid).display = False
            except Exception:
                pass
        target_id = screens.get(name, "#screen_chat")
        try:
            self.query_one(target_id).display = True
        except Exception:
            pass

        # Update nav button active state in chat screen sidebar
        try:
            chat = self.query_one("#screen_chat", ChatScreen)
            for btn in chat.query(".nav-item"):
                btn.remove_class("active")
            chat.query_one(f"#nav_{name}").add_class("active")
        except Exception:
            pass

    def switch_to(self, screen: str) -> None:
        """Public: switch screens from any child widget."""
        self._show_screen(screen)

    # ── Actions ──────────────────────────────────────────────────────────────

    def action_quit_app(self) -> None:
        self.exit()

    def action_go_chat(self) -> None:
        self._show_screen("chat")

    def action_go_automate(self) -> None:
        self._show_screen("automate")

    def action_go_tools(self) -> None:
        self._show_screen("tools")

    def action_go_settings(self) -> None:
        self._show_screen("settings")

    def action_new_session(self) -> None:
        store.create_session()
        try:
            chat = self.query_one("#screen_chat", ChatScreen)
            chat._current_messages = []
            chat._load_messages()
            chat._load_session_list()
        except Exception:
            pass
        self.notify("New session")


def main():
    """Entry point — instant boot."""
    app = ELEApp()
    app.run()


if __name__ == "__main__":
    main()