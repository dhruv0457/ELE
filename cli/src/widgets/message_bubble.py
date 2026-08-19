"""Message Bubble Widget - Professional Style"""
from textual.widgets import Static, Label
from textual.containers import Container, Vertical, Horizontal

from ..store import Message


class MessageBubble(Container):
    """Professional message bubble with metadata."""

    DEFAULT_CSS = """
    MessageBubble {
        margin: 1 2;
        padding: 0;
        border: none;
        background: transparent;
        width: 1fr;
    }

    .bubble-wrapper {
        width: 1fr;
        padding: 0;
    }

    .user-bubble {
        background: #1e88e5;
        color: #ffffff;
        margin: 0 0 0 6;
        padding: 1 2;
        max-width: 85%;
    }

    .assistant-bubble {
        background: #f8f9fa;
        color: #1a1a2e;
        margin: 0 6 0 0;
        padding: 1 2;
        border: solid #e0e4ec;
        max-width: 85%;
    }

    .message-meta {
        color: #8a8aa0;
        text-style: dim;
        margin-bottom: 1;
        height: 1;
    }

    .bubble-content {
    }

    .thought-preview {
        color: #8a8aa0;
        text-style: italic;
        margin: 1 0;
        padding-left: 1;
        border-left: solid #64b5f6;
        background: #f8f9fa;
    }

    .tool-preview {
        color: #f57f17;
        margin: 1 0;
        padding: 0 1;
        background: #f8f9fa;
        border-left: solid #f57f17;
    }

    .streaming-cursor {
        color: #1e88e5;
        text-style: bold blink;
    }

    .tools-used {
        margin-top: 1;
        height: auto;
    }

    .tool-badge {
        background: #64b5f6;
        color: #ffffff;
        padding: 0 1;
        margin-right: 1;
    }

    .message-time {
        color: #8a8aa0;
        text-style: dim;
    }

    .message-role {
        text-style: bold;
        color: #1e88e5;
    }
    """

    def __init__(self, message: 'Message'):
        super().__init__()
        self.message = message
        self.add_class("user-bubble" if message.role == "user" else "assistant-bubble")
        self.add_class("bubble-wrapper")

    def compose(self):
        role_label = "You" if self.message.role == "user" else "Ellie"
        time_str = self.message.timestamp.strftime("%H:%M") if hasattr(self.message, 'timestamp') and self.message.timestamp else ""

        yield Container(
            Horizontal(
                Label(f"{role_label}", classes="message-role"),
                Label(time_str, classes="message-time"),
                classes="message-meta",
            ),
            Label(self.message.content or "", classes="bubble-content", id="content"),
            id="bubble_main",
        )

        if self.message.thoughts:
            with Container(classes="thoughts-section"):
                yield Label(f"💭 Thoughts ({len(self.message.thoughts)})", classes="thought-preview")
                for thought in self.message.thoughts:
                    yield Label(f"  {thought}", classes="thought-line")

        if self.message.tools_used:
            yield Container(
                *[Label(f"⚙ {tool}", classes="tool-badge") for tool in self.message.tools_used],
                classes="tools-used",
            )

        if self.message.is_streaming:
            yield Label("▌", classes="streaming-cursor")

    def update_content(self, content: str):
        """Update message content (for streaming)"""
        try:
            content_label = self.query_one("#content", Label)
            content_label.update(content)
        except Exception:
            pass