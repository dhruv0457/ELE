"""Autonomous Mode Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ListView, ListItem, Label, Button
from textual import events

from ..store import store, OverlayStatus
from ..widgets.ellie_avatar import EllieAvatar


class AutonomousScreen(Container):
    """Autonomous Agent Mode Screen"""

    DEFAULT_CSS = """
    AutonomousScreen {
        layout: vertical;
        height: 1fr;
        display: none;
    }

    AutonomousScreen.visible {
        display: block;
    }

    #ellie_avatar {
        dock: top;
    }

    #execution_stream {
        height: 60%;
        border: solid $primary;
        margin: 1;
        padding: 1;
        overflow-y: auto;
    }

    #conversation_panel {
        height: 40%;
        border: solid $primary;
        margin: 1;
        padding: 1;
        overflow-y: auto;
    }

    .execution-line {
        margin: 0;
    }

    .command {
        color: $primary;
        text-style: bold;
    }

    .output {
        color: $text-muted;
    }

    .thought {
        color: $warning;
        text-style: italic;
    }

    .result {
        color: $success;
    }

    .error {
        color: $error;
    }

    .conversation-user {
        color: $primary;
        text-style: bold;
    }

    .conversation-assistant {
        color: $accent;
        text-style: bold;
    }
    """

    def compose(self):
        yield Static("🤖 Ellie ◉ Listening...", id="ellie_avatar")
        yield ListView(id="execution_stream")
        yield ListView(id="conversation_panel")

    def on_mount(self):
        self.start_voice_pipeline()

    def start_voice_pipeline(self):
        """Start the continuous voice pipeline"""
        store.overlay_status = OverlayStatus.LISTENING
        # TODO: Implement actual voice pipeline
        self.add_execution("System", "Autonomous mode started. Ellie is listening...", "system")
        self.add_conversation("Ellie", "I'm ready. What would you like me to do?", "assistant")

    def stop_voice_pipeline(self):
        """Stop the voice pipeline"""
        pass

    def add_execution(self, source: str, text: str, type: str = "output"):
        """Add line to execution stream"""
        from textual.widgets import ListItem, Label
        execution_list = self.query_one("#execution_stream")

        prefix = ""
        if source:
            prefix = f"{source}: "

        label = Label(f"{prefix}{text}", classes=f"execution-line {type}")
        execution_list.append(ListItem(label))
        execution_list.index = len(execution_list.children) - 1

    def add_conversation(self, speaker: str, text: str, role: str):
        """Add to conversation panel"""
        from textual.widgets import ListItem, Label
        conv_list = self.query_one("#conversation_panel")

        if role == "user":
            prefix = "👤 "
            cls = "conversation-user"
        else:
            prefix = "🤖 "
            cls = "conversation-assistant"

        label = Label(f"{prefix}{speaker}: {text}", classes=cls)
        conv_list.append(ListItem(label))
        conv_list.index = len(conv_list.children) - 1

    def on_key(self, event: events.Key):
        if event.key == "escape":
            self.app.action_exit_mode()