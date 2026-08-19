"""JARVIS-style Chat Screen — Hacker terminal aesthetic"""
import asyncio
import uuid
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Static, ListView, ListItem, Label, Markdown
from textual.binding import Binding

from ..store import store, Message, AgentStatus
from ..widgets.message_bubble import MessageBubble
from ..widgets.safe_text_area import SafeTextArea
from .. import llm as engine


class SessionListItem(ListItem):
    """Custom list item representing a session without hardcoded widget IDs."""
    def __init__(self, session_id: str, label_text: str) -> None:
        super().__init__(Label(label_text))
        self.session_id = session_id


class ChatScreen(Container):
    """Main JARVIS chat interface."""

    BINDINGS = [
        Binding("enter", "send", "Send", show=False),
        Binding("ctrl+l", "clear_chat", "Clear", show=False),
        Binding("ctrl+n", "new_session", "New Session", show=False),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._streaming = False
        self._current_messages: list = []  # conversation history for LLM

    def compose(self) -> ComposeResult:
        with Horizontal(id="chat_layout"):
            # ── Sidebar ─────────────────────────────────────────────
            with Vertical(id="sidebar"):
                yield Static("⚡ ELE", id="sidebar_logo")
                yield Static("─" * 18, classes="sidebar-divider")
                yield Button("󰭹  Chat", id="nav_chat", classes="nav-item active")
                yield Button("󰄙  Automate", id="nav_automate", classes="nav-item")
                yield Button("  Tools", id="nav_tools", classes="nav-item")
                yield Button("  Settings", id="nav_settings", classes="nav-item")
                yield Static("─" * 18, classes="sidebar-divider")
                yield Static("SESSIONS", classes="sidebar-section-title")
                yield ListView(id="session_list")
                yield Button("+ New", id="new_session_btn", classes="new-session-btn")

            # ── Main chat area ───────────────────────────────────────
            with Vertical(id="chat_main"):
                # Status bar
                yield Static("", id="chat_status_bar")
                # Messages
                yield ListView(id="messages_list")
                # Thinking panel (hidden by default)
                yield Static("", id="thinking_panel", classes="thinking-panel hidden")
                # Input bar
                with Horizontal(id="input_bar"):
                    yield SafeTextArea(id="input_area", tab_behavior="indent")
                    with Vertical(id="input_buttons"):
                        yield Button("▶", id="send_btn", classes="send-btn")
                        yield Button("🎤", id="voice_btn", classes="voice-btn")

    def on_mount(self) -> None:
        self._load_session_list()
        self._load_messages()
        self._update_status_bar()
        self.query_one("#input_area").focus()
        # Non-blocking: check LLM availability
        self.run_worker(self._init_llm(), exclusive=False)

    async def _init_llm(self) -> None:
        """Detect best available LLM and update status bar."""
        engine.reload_keys()
        provider, model = engine.get_best_provider()
        store.set_active_model(model, provider)
        store.set_agent_status(AgentStatus.IDLE)
        self._update_status_bar()

    def _update_status_bar(self) -> None:
        """Update top status bar with model and connection info."""
        try:
            status = self.query_one("#chat_status_bar", Static)
            provider = store.active_provider.upper() if store.active_provider else "NO KEY"
            model_short = store.active_model.split("/")[-1] if store.active_model else "—"
            connected_dot = "[#00FF9D]●[/]" if store.backend_connected else "[#FF3366]●[/]"
            be_label = "Backend: ON" if store.backend_connected else "Backend: OFF"

            # Agent status
            status_icons = {
                AgentStatus.IDLE: "[dim]idle[/]",
                AgentStatus.THINKING: "[#A855F7]thinking...[/]",
                AgentStatus.WORKING: "[#F59E0B]working...[/]",
                AgentStatus.STREAMING: "[#00FFE0]streaming[/]",
                AgentStatus.ERROR: "[#FF3366]error[/]",
            }
            agent_status = status_icons.get(store.agent_status, "[dim]idle[/]")

            tokens = store.token_usage["total"]
            token_str = f"[dim]{tokens:,} tokens[/]" if tokens > 0 else ""

            parts = [
                f"[bold #00FFE0]{provider}[/] [dim]·[/] [dim]{model_short}[/]",
                f"{connected_dot} [dim]{be_label}[/]",
                agent_status,
            ]
            if token_str:
                parts.append(token_str)

            status.update("  ".join(parts))
        except Exception:
            pass

    def _load_session_list(self) -> None:
        lst = self.query_one("#session_list", ListView)
        lst.clear()
        for sid, session in store.sessions.items():
            label = session.title[:16] + ("…" if len(session.title) > 16 else "")
            active = " ●" if sid == store.current_session_id else ""
            item = SessionListItem(sid, f"[dim]{label}{active}[/]")
            lst.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "session_list":
            item = event.item
            if isinstance(item, SessionListItem):
                sid = item.session_id
                if sid and sid in store.sessions and sid != store.current_session_id:
                    store.switch_session(sid)
                    self._load_messages()
                    self._load_session_list()

    def _load_messages(self) -> None:
        lst = self.query_one("#messages_list", ListView)
        lst.clear()
        self._current_messages = []
        for msg in store.messages:
            self._add_bubble(msg)
            self._current_messages.append({"role": msg.role, "content": msg.content})
        self._scroll_bottom()

    def _add_bubble(self, msg: Message) -> "MessageBubble":
        lst = self.query_one("#messages_list", ListView)
        bubble = MessageBubble(msg)
        item = ListItem(bubble)
        lst.append(item)
        self._scroll_bottom()
        return bubble

    def _scroll_bottom(self) -> None:
        try:
            lst = self.query_one("#messages_list", ListView)
            lst.scroll_end(animate=False)
        except Exception:
            pass

    def _set_thinking(self, visible: bool, text: str = "") -> None:
        try:
            panel = self.query_one("#thinking_panel", Static)
            if visible:
                panel.update(text)
                panel.remove_class("hidden")
            else:
                panel.add_class("hidden")
                panel.update("")
        except Exception:
            pass

    # ── Sending messages ─────────────────────────────────────────────────────

    async def send_message(self) -> None:
        if self._streaming:
            return
        input_area = self.query_one("#input_area", SafeTextArea)
        text = input_area.text.strip()
        if not text:
            return
        input_area.text = ""

        # Slash commands
        if text.startswith("/"):
            await self._handle_slash(text)
            return

        # Add user message
        user_msg = Message(role="user", content=text)
        store.add_message(user_msg)
        self._add_bubble(user_msg)
        self._current_messages.append({"role": "user", "content": text})

        # Add assistant placeholder
        asst_msg = Message(role="assistant", content="", is_streaming=True)
        store.add_message(asst_msg)
        bubble = self._add_bubble(asst_msg)

        self._streaming = True
        store.set_agent_status(AgentStatus.STREAMING)
        self._update_status_bar()

        try:
            await self._stream_response(text, asst_msg, bubble)
        finally:
            self._streaming = False
            store.set_agent_status(AgentStatus.IDLE)
            self._set_thinking(False)
            self._update_status_bar()
            self._load_session_list()

    async def _stream_response(
        self, user_text: str, msg: Message, bubble: "MessageBubble"
    ) -> None:
        thoughts_acc = ""
        accumulated = ""

        try:
            async for event in engine.stream_response(
                messages=self._current_messages,
                provider=store.active_provider or "auto",
                model=store.active_model or "auto",
            ):
                if event.type == "model_info":
                    store.set_active_model(event.model, store.active_provider)
                    self._update_status_bar()

                elif event.type == "thought":
                    thoughts_acc += event.content + " "
                    store.set_agent_status(AgentStatus.THINKING)
                    self._set_thinking(True, f"[#A855F7]🧠 Thinking:[/] [italic #A855F7]{thoughts_acc.strip()}[/]")
                    self._update_status_bar()

                elif event.type == "tool_start":
                    store.set_agent_status(AgentStatus.WORKING, event.tool)
                    self._set_thinking(
                        True,
                        f"[#F59E0B]⚙ Running:[/] [bold]{event.tool}[/]"
                    )
                    self._update_status_bar()

                elif event.type == "tool_end":
                    result_preview = event.content[:120]
                    self._set_thinking(
                        True,
                        f"[#00FF9D]✓ {event.tool}[/] [dim]→ {result_preview}[/]"
                    )
                    # Inject tool result into conversation context
                    self._current_messages.append({
                        "role": "assistant",
                        "content": f"TOOL_RESULT {event.tool}: {event.content}"
                    })
                    await asyncio.sleep(0.5)  # Brief pause so user can see result

                elif event.type == "delta":
                    accumulated += event.content
                    msg.content = accumulated
                    bubble.update_content(accumulated)
                    self._scroll_bottom()

                elif event.type == "final":
                    msg.content = accumulated or event.content
                    msg.is_streaming = False
                    bubble.update_content(msg.content, done=True)
                    # Append to conversation history
                    self._current_messages.append({
                        "role": "assistant",
                        "content": msg.content
                    })
                    self._scroll_bottom()
                    return

                elif event.type == "error":
                    msg.content = f"{event.content}"
                    msg.is_streaming = False
                    msg.error = True
                    bubble.update_content(msg.content, done=True, error=True)
                    self._scroll_bottom()
                    return

        except Exception as e:
            msg.content = f"⚠ Unexpected error: {e}"
            msg.is_streaming = False
            msg.error = True
            bubble.update_content(msg.content, done=True, error=True)

    # ── Slash commands ────────────────────────────────────────────────────────

    async def _handle_slash(self, cmd: str) -> None:
        parts = cmd.split(maxsplit=1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        responses = {
            "/help": (
                "**ELE Agent Commands**\n\n"
                "| Command | Action |\n"
                "|---------|--------|\n"
                "| `/help` | Show this help |\n"
                "| `/clear` | Clear chat |\n"
                "| `/model [name]` | Switch model |\n"
                "| `/models` | List available models |\n"
                "| `/keys` | Show API key status |\n"
                "| `/browse <url>` | Open URL in browser |\n"
                "| `/shell <cmd>` | Run a shell command |\n"
                "| `/new` | New session |\n"
            ),
            "/models": self._get_models_info(),
            "/keys": self._get_keys_info(),
        }

        if command == "/clear":
            store.clear_messages()
            self._current_messages = []
            self._load_messages()
            return

        if command == "/new":
            store.create_session()
            self._current_messages = []
            self._load_messages()
            self._load_session_list()
            self.app.notify("New session created")
            return

        if command == "/model" and arg:
            await self._switch_model(arg.strip())
            return

        if command == "/shell" and arg:
            import subprocess
            result = subprocess.run(arg, shell=True, capture_output=True, text=True, timeout=30)
            content = f"```\n$ {arg}\n{result.stdout or result.stderr or '(no output)'}\n```"
            msg = Message(role="assistant", content=content)
            store.add_message(msg)
            self._add_bubble(msg)
            return

        if command == "/browse" and arg:
            import webbrowser
            webbrowser.open(arg)
            msg = Message(role="assistant", content=f"Opened [{arg}]({arg}) in browser.")
            store.add_message(msg)
            self._add_bubble(msg)
            return

        content = responses.get(command, f"Unknown command: `{command}`. Type `/help` for commands.")
        msg = Message(role="assistant", content=content)
        store.add_message(msg)
        self._add_bubble(msg)

    def _get_models_info(self) -> str:
        engine.reload_keys()
        providers = engine.get_available_providers()
        lines = ["**Available Providers & Models**\n"]
        model_map = {
            "nvidia": "nvidia/llama-3.3-70b-instruct, nvidia/nemotron-4-340b",
            "gemini": "gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash",
            "openai": "gpt-4o, gpt-4o-mini, gpt-3.5-turbo",
            "anthropic": "claude-3-5-sonnet-20241022, claude-3-haiku-20240307",
            "groq": "llama3-70b-8192, mixtral-8x7b-32768",
            "ollama": "llama3, mistral, codellama (local)",
        }
        for p in providers:
            icon = "✅" if p != "ollama" else "🟡"
            models = model_map.get(p, "—")
            lines.append(f"**{icon} {p.upper()}**: {models}")
        return "\n".join(lines)

    def _get_keys_info(self) -> str:
        engine.reload_keys()
        lines = ["**API Key Status**\n"]
        key_map = [
            ("NVIDIA_API_KEY", "NVIDIA"),
            ("OPENAI_API_KEY", "OpenAI"),
            ("GEMINI_API_KEY", "Gemini"),
            ("ANTHROPIC_API_KEY", "Anthropic"),
            ("GROQ_API_KEY", "Groq"),
        ]
        for env_key, label in key_map:
            val = engine._KEYS.get(env_key, "")
            if val:
                masked = val[:4] + "..." + val[-4:] if len(val) > 8 else "****"
                lines.append(f"✅ **{label}**: `{masked}`")
            else:
                lines.append(f"❌ **{label}**: not set")
        lines.append(
            "\n_Add keys via **Settings (Ctrl+4)**, `ele setup`, or in `~/.ele-agent/.env`._"
        )
        return "\n".join(lines)

    async def _switch_model(self, model_str: str) -> None:
        """Parse 'provider/model' or just 'provider'."""
        if "/" in model_str:
            parts = model_str.split("/", 1)
            provider = parts[0].lower()
            model = model_str
        else:
            provider = model_str.lower()
            model = engine._default_model_for(provider)
        store.set_active_model(model, provider)
        self._update_status_bar()
        msg = Message(role="assistant", content=f"Switched to **{provider.upper()}** — `{model}`")
        store.add_message(msg)
        self._add_bubble(msg)

    # ── Button handlers ───────────────────────────────────────────────────────

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "send_btn":
            await self.send_message()
        elif btn_id == "voice_btn":
            self._toggle_voice()
        elif btn_id == "new_session_btn":
            store.create_session()
            self._current_messages = []
            self._load_messages()
            self._load_session_list()
        elif btn_id and btn_id.startswith("nav_"):
            screen = btn_id.replace("nav_", "")
            self.app.switch_to(screen)

    def _toggle_voice(self) -> None:
        store.voice_listening = not store.voice_listening
        btn = self.query_one("#voice_btn", Button)
        if store.voice_listening:
            btn.label = "🔴"
            self.app.notify("🎤 Voice listening ON")
        else:
            btn.label = "🎤"
            self.app.notify("Voice OFF")

    # ── Key bindings ──────────────────────────────────────────────────────────

    def action_send(self) -> None:
        self.run_worker(self.send_message())

    def action_clear_chat(self) -> None:
        store.clear_messages()
        self._current_messages = []
        self._load_messages()

    def action_new_session(self) -> None:
        store.create_session()
        self._current_messages = []
        self._load_messages()
        self._load_session_list()