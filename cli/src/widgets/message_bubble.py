"""Message Bubble widget — JARVIS hacker style"""
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Markdown, Static
from datetime import datetime
from ..store import Message


class MessageBubble(Container):
    """A single chat message bubble."""

    DEFAULT_CSS = """
    MessageBubble {
        width: 1fr;
        padding: 0;
        margin: 0 0 1 0;
        border: none;
        background: transparent;
    }
    MessageBubble .bubble-header {
        height: 1;
        layout: horizontal;
    }
    MessageBubble .role-label {
        text-style: bold;
        width: auto;
        padding-right: 1;
    }
    MessageBubble .time-label {
        color: #475569;
        width: auto;
    }
    MessageBubble .bubble-content {
        padding: 0 2;
    }
    MessageBubble .tool-badge {
        color: #F59E0B;
        padding: 0 1;
        margin-top: 0;
        height: 1;
    }
    MessageBubble .thought-line {
        color: #A855F7;
        text-style: italic;
        padding: 0 2;
        height: auto;
    }
    MessageBubble .streaming-cursor {
        color: #00FFE0;
        text-style: bold;
    }
    MessageBubble.user-bubble {
        border-left: wide #00FF9D;
        background: #0D1117;
        padding-left: 1;
    }
    MessageBubble.assistant-bubble {
        border-left: wide #00FFE0;
        background: #0A0F1E;
        padding-left: 1;
    }
    MessageBubble.error-bubble {
        border-left: wide #FF3366;
        background: #1A0A0A;
        padding-left: 1;
    }
    """

    def __init__(self, message: Message, **kwargs) -> None:
        super().__init__(**kwargs)
        self.message = message
        if message.role == "user":
            self.add_class("user-bubble")
        elif message.error:
            self.add_class("error-bubble")
        else:
            self.add_class("assistant-bubble")

    def compose(self) -> ComposeResult:
        # Header row: role + timestamp
        with Horizontal(classes="bubble-header"):
            if self.message.role == "user":
                yield Label("[bold #00FF9D]❯ YOU[/]", classes="role-label")
            else:
                yield Label("[bold #00FFE0]⚡ ELE[/]", classes="role-label")
            ts = getattr(self.message, "timestamp", datetime.now())
            if hasattr(ts, "strftime"):
                time_str = ts.strftime("%H:%M")
            else:
                time_str = ""
            yield Label(f"[dim]{time_str}[/]", classes="time-label")

        # Thoughts
        if self.message.thoughts:
            yield Static(
                f"[italic #A855F7]🧠 {' · '.join(self.message.thoughts[:2])}[/]",
                classes="thought-line"
            )

        # Tools used
        for tool in self.message.tools_used:
            yield Static(f"[#F59E0B]⚙ {tool}[/]", classes="tool-badge")

        # Content
        yield Markdown(self.message.content or " ", id="content", classes="bubble-content")

        # Streaming cursor
        if getattr(self.message, "is_streaming", False):
            yield Static("█", classes="streaming-cursor", id="cursor")

    def update_content(self, content: str, done: bool = False, error: bool = False) -> None:
        """Update message content in-place."""
        try:
            md = self.query_one("#content", Markdown)
            md.update(content or " ")
        except Exception:
            pass

        if done:
            self.message.is_streaming = False
            try:
                cursor = self.query("#cursor")
                for c in cursor:
                    c.remove()
            except Exception:
                pass
            if error:
                self.remove_class("assistant-bubble")
                self.add_class("error-bubble")