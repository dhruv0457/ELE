"""Chat Screen - Professional Right-Side Layout with Thinking Panel"""
import asyncio
import uuid
from datetime import datetime

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ListView, ListItem, Button, Label, RichLog
from ..widgets.safe_text_area import SafeTextArea
from textual import events

from ..store import store, Message
from ..widgets.message_bubble import MessageBubble
from .. import backend as be


class ChatScreen(Container):
    """Chat Mode Screen - Professional right-side chat layout with thinking panel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token = None
        self._session_id = None
        self._auth_task = None
        self._streaming = False

    def compose(self):
        # Left sidebar
        yield Container(
            Static("💬 ELE", classes="sidebar-title"),
            Button("💬 Chat", id="nav_chat", classes="sidebar-item -active"),
            Button("📋 Sessions", id="nav_sessions", classes="sidebar-item"),
            Button("🔧 Tools", id="nav_tools", classes="sidebar-item"),
            Button("🔌 Plugins", id="nav_plugins", classes="sidebar-item"),
            Button("⚙ Settings", id="nav_settings", classes="sidebar-item"),
            classes="sidebar",
        )

        # Right chat area - with thinking panel
        yield Container(
            Static("● Connecting...", id="status_line", classes="status-line"),
            Container(
                ListView(id="messages_list"),
                id="messages_container",
            ),
            # Thinking panel - shows live thoughts
            Static("", id="thinking_panel", classes="thinking-panel"),
            Container(
                Horizontal(
                    SafeTextArea(id="input_area", placeholder="Ask anything... (Enter to send)"),
                    Button("🎤", id="voice_btn"),
                    Button("Send", id="send_btn", classes="-primary"),
                    classes="input_row",
                ),
                id="input_bar",
            ),
            id="chat_main",
        )

    def on_mount(self):
        self.load_messages()
        self._auth_task = asyncio.create_task(self._connect_backend())
        self.call_later(self._focus_input)

    def _focus_input(self):
        try:
            self.query_one("#input_area").focus()
        except Exception:
            pass

    async def _connect_backend(self):
        status = self.query_one("#status_line", Static)
        try:
            if not be.is_backend_up():
                status.update("● Backend: NOT running (start backend on :8000)")
                store.set_backend_status(False, "down")
                return
            tok = be.login_or_register()
            self._token = tok["access_token"]
            self._session_id = f"session_{uuid.uuid4().hex[:8]}"
            store.set_backend_status(True, "connected")
            status.update(f"● Backend: connected as {tok['email']}")
        except Exception as e:
            store.set_backend_status(False, "error")
            status.update(f"● Backend: error - {e}")

    def load_messages(self):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        messages_list.clear()
        for msg in store.messages:
            messages_list.append(ListItem(MessageBubble(msg)))
        self.call_later(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        try:
            messages_list = self.query_one("#messages_list", expect_type=ListView)
            if messages_list.children:
                messages_list.index = len(messages_list.children) - 1
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            await self.send_message()
        elif event.button.id == "voice_btn":
            self.toggle_voice()
            event.button.toggle_class("-active")
        elif event.button.id.startswith("nav_"):
            self._switch_sidebar(event.button.id)

    def _switch_sidebar(self, nav_id: str):
        for btn_id in ["nav_chat", "nav_sessions", "nav_tools", "nav_plugins", "nav_settings"]:
            try:
                btn = self.query_one(f"#{btn_id}")
                btn.remove_class("-active")
            except Exception:
                pass
        try:
            self.query_one(f"#{nav_id}").add_class("-active")
        except Exception:
            pass

        screen_map = {
            "nav_chat": "chat",
            "nav_sessions": "chat",
            "nav_tools": "tools",
            "nav_plugins": "plugins",
            "nav_settings": "settings",
        }
        screen = screen_map.get(nav_id)
        if screen and screen != "chat":
            self.app.switch_screen(screen)

    async def on_text_area_submitted(self, event):
        await self.send_message()

    async def send_message(self):
        input_area = self.query_one("#input_area")
        text = input_area.text.strip()
        if not text:
            return
        input_area.clear()

        # Add user message
        user_msg = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="user",
            content=text,
            timestamp=datetime.now(),
        )
        store.add_message(user_msg)
        self.add_message_bubble(user_msg)

        if not self._token and self._auth_task is not None:
            try:
                await asyncio.wait_for(asyncio.shield(self._auth_task), timeout=15)
            except (asyncio.TimeoutError, Exception):
                pass

        # Create streaming assistant message
        thinking_msg = Message(
            id="thinking",
            role="assistant",
            content="",
            is_streaming=True,
            timestamp=datetime.now(),
        )
        store.add_message(thinking_msg)
        bubble = self.add_message_bubble(thinking_msg)

        if not self._token:
            thinking_msg.content = "Backend not connected. Start it on :8000."
            thinking_msg.is_streaming = False
            self._refresh_bubble(bubble, thinking_msg)
            return

        self._streaming = True
        asyncio.create_task(self._stream_response(text, thinking_msg, bubble))

    def add_message_bubble(self, msg):
        bubble = MessageBubble(msg)
        self.query_one("#messages_list").append(ListItem(bubble))
        self.scroll_to_bottom()
        return bubble

    def _refresh_bubble(self, bubble, msg):
        try:
            bubble.update_content(msg.content)
        except Exception:
            pass

    def _update_thinking_panel(self, thoughts_acc, tools_acc, current_tool=None):
        """Update the thinking panel with live thoughts."""
        thinking_panel = self.query_one("#thinking_panel", Static)
        lines = []
        
        if thoughts_acc:
            lines.append("[bold]💭 Thinking:[/bold]")
            for t in thoughts_acc[-5:]:  # Show last 5 thoughts
                lines.append(f"  {t}")
        
        if tools_acc:
            lines.append("")
            lines.append("[bold]⚙️ Tools:[/bold]")
            for tool in tools_acc:
                lines.append(f"  ⚙ {tool}")
        
        if current_tool:
            lines.append("")
            lines.append(f"[bold yellow]▶ Running: {current_tool}[/bold yellow]")
        
        thinking_panel.update("\n".join(lines) if lines else "")

    async def _stream_response(self, user_text, thinking_msg, bubble):
        thoughts_acc = []
        tools_acc = []
        content_acc = ""

    def _refresh_bubble(self, bubble, msg):
        try:
            bubble.update_content(msg.content)
        except Exception:
            pass

    def add_message_bubble(self, msg):
        bubble = MessageBubble(msg)
        self.query_one("#messages_list").append(ListItem(bubble))
        self.scroll_to_bottom()
        return bubble

    def scroll_to_bottom(self):
        try:
            messages_list = self.query_one("#messages_list", expect_type=ListView)
            if messages_list.children:
                messages_list.index = len(messages_list.children) - 1
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            await self.send_message()
        elif event.button.id == "voice_btn":
            self.toggle_voice()
            event.button.toggle_class("-active")
        elif event.button.id.startswith("nav_"):
            self._switch_sidebar(event.button.id)

    def _switch_sidebar(self, nav_id: str):
        for btn_id in ["nav_chat", "nav_sessions", "nav_tools", "nav_plugins", "nav_settings"]:
            try:
                btn = self.query_one(f"#{btn_id}")
                btn.remove_class("-active")
            except Exception:
                pass
        try:
            self.query_one(f"#{nav_id}").add_class("-active")
        except Exception:
            pass

        screen_map = {
            "nav_chat": "chat",
            "nav_sessions": "chat",
            "nav_tools": "tools",
            "nav_plugins": "plugins",
            "nav_settings": "settings",
        }
        screen = screen_map.get(nav_id)
        if screen and screen != "chat":
            self.app.switch_screen(screen)

    async def on_text_area_submitted(self, event):
        await self.send_message()

    async def _connect_backend(self):
        status = self.query_one("#status_line", Static)
        try:
            if not be.is_backend_up():
                status.update("● Backend: NOT running (start backend on :8000)")
                store.set_backend_status(False, "down")
                return
            tok = be.login_or_register()
            self._token = tok["access_token"]
            self._session_id = f"session_{uuid.uuid4().hex[:8]}"
            store.set_backend_status(True, "connected")
            status.update(f"● Backend: connected as {tok['email']}")
        except Exception as e:
            store.set_backend_status(False, "error")
            status.update(f"● Backend: error - {e}")

    def load_messages(self):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        messages_list.clear()
        for msg in store.messages:
            messages_list.append(ListItem(MessageBubble(msg)))
        self.call_later(self.scroll_to_bottom)

    def scroll_to_bottom(self):
        try:
            messages_list = self.query_one("#messages_list", expect_type=ListView)
            if messages_list.children:
                messages_list.index = len(messages_list.children) - 1
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "send_btn":
            await self.send_message()
        elif event.button.id == "voice_btn":
            self.toggle_voice()
            event.button.toggle_class("-active")
        elif event.button.id.startswith("nav_"):
            self._switch_sidebar(event.button.id)

    def _switch_sidebar(self, nav_id: str):
        for btn_id in ["nav_chat", "nav_sessions", "nav_tools", "nav_plugins", "nav_settings"]:
            try:
                btn = self.query_one(f"#{btn_id}")
                btn.remove_class("-active")
            except Exception:
                pass
        try:
            self.query_one(f"#{nav_id}").add_class("-active")
        except Exception:
            pass

        screen_map = {
            "nav_chat": "chat",
            "nav_sessions": "chat",
            "nav_tools": "tools",
            "nav_plugins": "plugins",
            "nav_settings": "settings",
        }
        screen = screen_map.get(nav_id)
        if screen and screen != "chat":
            self.app.switch_screen(screen)

    async def on_text_area_submitted(self, event):
        await self.send_message()

    def toggle_voice(self):
        store.voice_listening = not store.voice_listening
        self.notify("Voice " + ("enabled" if store.voice_listening else "disabled"))