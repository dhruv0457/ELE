"""Chat Screen"""
import asyncio
import uuid

from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, ListView, ListItem, TextArea, Button, Label
from textual import events

from ..store import store, Message
from ..widgets.message_bubble import MessageBubble
from .. import backend as be


class ChatScreen(Container):
    """Chat Mode Screen - talks to the backend over WebSocket."""

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

    .status-line {
        color: $text-muted;
        text-style: dim;
        height: 1;
    }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token = None
        self._session_id = None
        self._auth_task = None

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
                Static("Backend: connecting...", id="status_line", classes="status-line"),
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
        self._auth_task = asyncio.create_task(self._connect_backend())

    async def _connect_backend(self):
        status = self.query_one("#status_line", Static)
        try:
            if not be.is_backend_up():
                status.update("Backend: NOT running. Start with: python -m uvicorn app.main:app --port 8000")
                store.set_backend_status(False, "down")
                return
            tok = be.login_or_register()
            self._token = tok["access_token"]
            self._session_id = f"session_{uuid.uuid4().hex[:8]}"
            store.set_backend_status(True, "connected")
            status.update(f"Backend: connected as {tok['email']}")
        except Exception as e:
            store.set_backend_status(False, "error")
            status.update(f"Backend: error - {e}")

    def load_messages(self):
        messages_list = self.query_one("#messages_list", expect_type=ListView)
        messages_list.clear()
        for msg in store.messages:
            self.query_one("#messages_list").append(ListItem(MessageBubble(msg)))
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

        user_msg = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="user",
            content=text,
        )
        store.add_message(user_msg)
        self.add_message_bubble(user_msg)

        if not self._token and self._auth_task is not None:
            try:
                await asyncio.wait_for(asyncio.shield(self._auth_task), timeout=15)
            except (asyncio.TimeoutError, Exception):
                pass

        thinking_msg = Message(
            id="thinking",
            role="assistant",
            content="...",
            is_streaming=True,
        )
        store.add_message(thinking_msg)
        bubble = self.add_message_bubble(thinking_msg)

        if not self._token:
            thinking_msg.content = "Backend not connected. Start it on :8000."
            thinking_msg.is_streaming = False
            self._refresh_bubble(bubble, thinking_msg)
            return

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

    async def _stream_response(self, user_text, thinking_msg, bubble):
        """Stream events from the backend and update the thinking bubble live."""
        thoughts_acc = []
        tools_acc = []
        content_acc = ""

        try:
            async for evt in be.stream_chat(
                user_text, self._token, session_id=self._session_id,
            ):
                t = evt.get("type")
                if t == "thought":
                    thoughts_acc.append(evt.get("content", ""))
                    preview = "...\n".join(f"◉ {x}" for x in thoughts_acc[-3:])
                    thinking_msg.content = preview + "\n(thinking...)"
                    self._refresh_bubble(bubble, thinking_msg)
                elif t == "tool_start":
                    tools_acc.append(evt.get("tool", ""))
                    thinking_msg.content = (
                        "...\n".join(f"◉ {x}" for x in thoughts_acc[-3:])
                        + f"\n🔧 running {evt.get('tool')}..."
                    )
                    self._refresh_bubble(bubble, thinking_msg)
                elif t == "tool_result":
                    out = evt.get("output") or evt.get("error") or ""
                    if isinstance(out, str):
                        out = out[:200].replace("\n", " ")
                    thinking_msg.content = (
                        "...\n".join(f"◉ {x}" for x in thoughts_acc[-3:])
                        + f"\n🔧 {evt.get('tool')} -> {out}"
                    )
                    self._refresh_bubble(bubble, thinking_msg)
                elif t == "final":
                    content_acc = evt.get("content", "")
                    meta = evt.get("metadata", {}) or {}
                    if meta.get("thoughts"):
                        thoughts_acc = meta["thoughts"]
                    if meta.get("tools_used"):
                        tools_acc = meta["tools_used"]
                    break
                elif t == "error":
                    content_acc = f"[error] {evt.get('message', 'unknown')}"
                    break
        except Exception as e:
            content_acc = f"[error] connection failed: {e}"

        thinking_msg.id = f"msg_{uuid.uuid4().hex[:8]}"
        thinking_msg.content = content_acc or "(no response)"
        thinking_msg.thoughts = thoughts_acc
        thinking_msg.tools_used = tools_acc
        thinking_msg.is_streaming = False
        self._refresh_bubble(bubble, thinking_msg)

    def toggle_voice(self):
        store.voice_listening = not store.voice_listening
        self.notify("Voice " + ("enabled" if store.voice_listening else "disabled"))
