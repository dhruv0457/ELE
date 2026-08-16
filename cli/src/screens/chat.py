"""Chat Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ListView, ListItem, TextArea, Button
from textual import events

from ..store import store
from ..widgets.message_bubble import MessageBubble


class ChatScreen(Container):
    """Chat Mode Screen"""

    DEFAULT_CSS = """
    ChatScreen {
        layout: horizontal;
        height: 1fr;
    }

    .sidebar {
        width: 40;
        border-right: solid $primary;
        padding: 1;
        height: 1fr;
        overflow-y: auto;
    }

    .sidebar-title {
        text-style: bold;
        color: $primary;
        margin: 1 0;
    }

    .chat_area {
        width: 1fr;
        layout: vertical;
        height: 1fr;
    }

    #messages_container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #messages_list {
        height: 1fr;
    }

    #input_bar {
        height: auto;
        min-height: 5;
        border-top: solid $primary;
        padding: 1;
    }

    .input_area {
        width: 1fr;
        min-height: 3;
    }

    .voice_btn, .send_btn {
        margin-left: 1;
    }
    """

    def compose(self):
        yield Container(
            Static("💬 Chat", classes="sidebar-title"),
            Static("📋 Sessions", classes="sidebar-title"),
            Static("🔧 Tools", classes="sidebar-title"),
            Static("🔌 Plugins", classes="sidebar-title"),
            Static("⚙ Settings", classes="sidebar-title"),
            classes="sidebar",
        )
        yield Container(
            Container(
                ListView(id="messages_list"),
                id="messages_container",
            ),
            Container(
                Horizontal(
                    TextArea(id="input_area", classes="input_area"),
                    Button("🎤", id="voice_btn", classes="voice_btn"),
                    Button("Send", id="send_btn", classes="send_btn"),
                ),
                id="input_bar",
            ),
            id="chat_area",
        )

    def on_mount(self):
        self.load_messages()

    def load_messages(self):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        messages_list.clear()

        for msg in store.messages:
            bubble = MessageBubble(msg)
            self.query_one("#messages_list").append(ListItem(bubble))

        self.call_later(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        if messages_list.children:
            messages_list.index = len(messages_list.children) - 1

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            await self.send_message()
        elif event.button.id == "voice_btn":
            self.toggle_voice()

    async def on_text_area_submitted(self, event):
        await self.send_message()

    async def send_message(self):
        input_area = self.query_one("#input_area")
        text = input_area.text.strip()
        if not text:
            return

        input_area.clear()

        from ..store import Message
        import uuid

        user_msg = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="user",
            content=text,
        )
        store.add_message(user_msg)
        self.add_message_bubble(user_msg)

        self.show_thinking()
        self.simulate_response(text)

    def add_message_bubble(self, msg):
        from ..widgets.message_bubble import MessageBubble
        from textual.widgets import ListItem
        bubble = MessageBubble(msg)
        self.query_one("#messages_list").append(ListItem(bubble))
        self.scroll_to_bottom()

    def show_thinking(self):
        from ..store import Message
        thinking_msg = Message(
            id="thinking",
            role="assistant",
            content="",
            is_streaming=True,
        )
        store.add_message(thinking_msg)
        self.add_message_bubble(thinking_msg)

    def simulate_response(self, user_text: str):
        import asyncio

        async def delayed_response():
            await asyncio.sleep(1)
            from ..store import Message
            import uuid

            # Remove thinking message
            store.messages = [m for m in store.messages if m.id != "thinking"]

            response = f"I'll help you with: {user_text}\n\nHere's a sample response with code:\n\n```python\ndef hello():\n    print('Hello, World!')\n```"
            msg = Message(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                role="assistant",
                content=response,
                thoughts=["Planning response", "Generating code example"],
                tools_used=["file", "shell"],
            )
            store.add_message(msg)
            self.add_message_bubble(msg)

        asyncio.create_task(delayed_response())

    def toggle_voice(self):
        store.voice_listening = not store.voice_listening
        self.notify("Voice " + ("enabled" if store.voice_listening else "disabled"))