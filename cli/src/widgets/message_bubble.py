"""Message Bubble Widget"""
from textual.widgets import Static, Label, Button, Collapsible
from textual.containers import Container, Horizontal, Vertical
from textual import events

from ..store import Message


class MessageBubble(Container):
    """Message bubble with rich metadata"""

    DEFAULT_CSS = """
    MessageBubble {
        margin: 1;
        padding: 1;
        border: solid $primary;
        background: $surface;
    }

    .user-message {
        background: $primary;
        color: $text;
        margin-left: 20%;
    }

    .assistant-message {
        background: $surface;
        border: solid $primary;
    }

    .message-header {
        height: auto;
        margin-bottom: 1;
    }

    .message-role {
        text-style: bold;
        color: $primary;
    }

    .message-time {
        color: $text-muted;
        text-style: dim;
    }

    .message-content {
        margin: 1 0;
        white-space: pre-wrap;
    }

    .thoughts-section {
        border-left: solid $primary;
        margin-left: 1;
        padding-left: 1;
    }

    .thought-line {
        color: $text-muted;
    }

    .tools-used {
        margin-top: 1;
    }

    .tool-badge {
        background: $primary;
        color: $text;
        padding: 0 1;
        margin-right: 1;
    }

    .streaming-indicator {
        color: $warning;
        text-style: bold blink;
    }
    """

    def __init__(self, message: 'Message'):
        super().__init__()
        self.message = message
        self.add_class("user-message" if message.role == "user" else "assistant-message")

    def compose(self):
        role_label = "👤 You" if self.message.role == "user" else "🤖 Ellie"
        time_str = self.message.timestamp.strftime("%H:%M:%S")

        yield Container(
            Label(f"{role_label} • {time_str}", classes="message-header"),
            Label(self.message.content or "", classes="message-content", id="content"),
            id="message_main",
        )

        if self.message.thoughts:
            with Collapsible(title=f"Thoughts ({len(self.message.thoughts)})", collapsed=True):
                for thought in self.message.thoughts:
                    yield Label(f"◉ {thought}", classes="thought-line")

        if self.message.tools_used:
            yield Container(
                *[Label(f"🔧 {tool}", classes="tool-badge") for tool in self.message.tools_used],
                classes="tools-used",
            )

        if self.message.is_streaming:
            yield Label("▌ Streaming...", classes="streaming-indicator")

    def update_content(self, content: str):
        """Update message content (for streaming)"""
        content_label = self.query_one("#content", Label)
        content_label.update(content)