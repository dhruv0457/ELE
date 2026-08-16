"""Status Bar Widget"""
from textual.widgets import Static
from textual.containers import Horizontal

from ..store import store


class StatusBar(Static):
    """Status bar with connection, model, credits, battery, voice, time"""

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $surface;
        border-top: solid $primary;
        padding: 0 1;
    }

    .status-item {
        margin-right: 2;
    }

    .status-connected {
        color: $success;
    }

    .status-disconnected {
        color: $error;
    }
    """

    def on_mount(self):
        self.update_status()
        self.set_interval(1, self.update_status)

    def update_status(self):
        # Connection
        conn_status = "●" if store.backend_connected else "○"
        conn_class = "status-connected" if store.backend_connected else "status-disconnected"

        # Model (from config)
        model = "Auto (Gemini)"

        # Credits
        credits = "▲ 3/10"

        # Battery (placeholder)
        battery = "🔋 100%"

        # Voice
        voice = "🎤 On" if store.voice_listening else "🎤 Off"

        # Time
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M")

        self.update(
            f"[{conn_class}]{conn_status}[/] {model} {credits} {battery} {voice} {time_str}"
        )