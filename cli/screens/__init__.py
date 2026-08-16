"""Chat Screen"""
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Label, Button, Input, TextArea, ListView, ListItem
from textual.screen import Screen
from textual import events

from cli.store import store, Message
from cli.widgets.message_bubble import MessageBubble


class ChatScreen(Container):
    """Chat Mode Screen"""

    def compose(self):
        yield Container(
            # Sidebar
            Container(
                Static("💬 Chat", classes="sidebar-title"),
                Static("📋 Sessions", classes="sidebar-title"),
                Static("🔧 Tools", classes="sidebar-title"),
                Static("🔌 Plugins", classes="sidebar-title"),
                Static("⚙ Settings", classes="sidebar-title"),
                classes="sidebar",
            ),
            # Main chat area
            Container(
                # Messages
                Container(
                    ListView(id="messages_list"),
                    id="messages_container",
                ),
                # Input bar
                Container(
                    Horizontal(
                        TextArea(id="input_area", classes="input_area"),
                        Button("🎤", id="voice_btn", classes="voice_btn"),
                        Button("Send", id="send_btn", classes="send_btn"),
                    ),
                    id="input_bar",
                ),
                id="chat_area",
            ),
            classes="chat_layout",
        )

    def on_mount(self):
        self.load_messages()

    def load_messages(self):
        """Load messages from store"""
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        messages_list.clear()

        for msg in store.messages:
            bubble = MessageBubble(msg)
            messages_list.append(ListItem(bubble))

        # Scroll to bottom
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

    async def on_text_area_submitted(self, event: TextArea.Submitted):
        await self.send_message()

    async def send_message(self):
        input_area = self.query_one("#input_area", expect_type=TextArea)
        text = input_area.text.strip()
        if not text:
            return

        input_area.clear()

        # Add user message
        from cli.store import store, Message
        import uuid
        user_msg = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="user",
            content=text,
        )
        store.add_message(user_msg)
        self.add_message_bubble(user_msg)

        # Show loading
        self.show_thinking()

        # Send to backend via WebSocket
        # TODO: Implement WebSocket connection
        self.simulate_response(text)

    def add_message_bubble(self, msg):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        bubble = MessageBubble(msg)
        messages_list.append(ListItem(bubble))
        self.scroll_to_bottom()

    def show_thinking(self):
        """Show thinking indicator"""
        from cli.store import Message
        thinking_msg = Message(
            id="thinking",
            role="assistant",
            content="",
            is_streaming=True,
        )
        store.add_message(thinking_msg)
        self.add_message_bubble(thinking_msg)

    def simulate_response(self, user_text: str):
        """Simulate assistant response for demo"""
        import asyncio

        async def delayed_response():
            await asyncio.sleep(1)
            from cli.store import store, Message
            import uuid

            # Remove thinking message
            store.messages = [m for m in store.messages if m.id != "thinking"]

            # Add response
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
        from cli.store import store
        store.voice_listening = not store.voice_listening
        self.notify("Voice " + ("enabled" if store.voice_listening else "disabled"))

    def on_key(self, event: events.Key):
        """Handle key events"""
        if event.key == "escape":
            self.app.action_exit_mode()