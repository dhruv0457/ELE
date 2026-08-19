from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, ListView, ListItem, Label
from textual import events

class AutonomousScreen(Container):
    DEFAULT_CSS = """
    AutonomousScreen {
        layout: vertical;
        height: 1fr;
        display: none;
        background: #0A0E17;
    }
    AutonomousScreen.visible {
        display: block;
    }
    #execution_stream, #conversation_panel {
        background: #111622;
        border: solid #00FFE0;
        overflow: auto;
        height: 1fr;
        margin: 1;
        padding: 1;
    }
    .command { color: #00FFE0; text-style: bold; }
    .output { color: #8F9BA8; }
    .thought { color: #FFB800; text-style: italic; }
    .result { color: #00FF9D; }
    .error { color: #FF3366; }
    .conversation-user { color: #00FFE0; text-style: bold; }
    .conversation-assistant { color: #A855F7; text-style: bold; }
    """

    def compose(self) -> ComposeResult:
        yield Static("🤖 AGENT MODE ACTIVE", id="agent_indicator", classes="command")
        yield ListView(id="execution_stream")
        yield ListView(id="conversation_panel")

    def start_voice_pipeline(self) -> None:
        pass

    def stop_voice_pipeline(self) -> None:
        pass

    def add_execution(self, source: str, text: str, exec_type: str) -> None:
        list_view = self.query_one("#execution_stream", ListView)
        css_class = exec_type
        list_view.append(ListItem(Label(f"[{source}] {text}", classes=css_class)))
        list_view.scroll_end(animate=False)

    def add_conversation(self, speaker: str, text: str, role: str) -> None:
        list_view = self.query_one("#conversation_panel", ListView)
        css_class = f"conversation-{role}"
        list_view.append(ListItem(Label(f"{speaker}: {text}", classes=css_class)))
        list_view.scroll_end(animate=False)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.remove_class("visible")
            self.stop_voice_pipeline()