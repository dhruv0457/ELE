"""CLI Store - Central State Management"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ViewMode(str, Enum):
    CHAT = "chat"
    AUTOMATE = "automate"
    TOOLS = "tools"
    SETTINGS = "settings"


class AgentStatus(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class Message:
    role: str          # user | assistant | system | tool
    content: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    thoughts: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    is_streaming: bool = False
    model: str = ""
    error: bool = False


@dataclass
class Session:
    id: str = field(default_factory=lambda: f"ses_{uuid.uuid4().hex[:8]}")
    title: str = "New Session"
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class Store:
    """Central state for the ELE Agent CLI"""

    def __init__(self):
        # View
        self.mode: ViewMode = ViewMode.CHAT

        # Agent state
        self.agent_status: AgentStatus = AgentStatus.IDLE
        self.current_tool: str = ""
        self.thoughts_buffer: List[str] = []

        # Sessions
        self.sessions: Dict[str, Session] = {}
        self.current_session_id: Optional[str] = None

        # Messages shortcut (points to current session's messages)
        self.messages: List[Message] = []

        # Voice
        self.voice_listening: bool = False
        self.voice_enabled: bool = False

        # Backend / LLM
        self.backend_connected: bool = False
        self.backend_status: str = "offline"
        self.active_model: str = "auto"
        self.active_provider: str = ""

        # Token tracking
        self.token_usage: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}

        # Execution log (Automate mode)
        self.execution_log: List[Dict[str, Any]] = []

        # Initialize with a default session
        self._init_default_session()

    def _init_default_session(self) -> None:
        s = Session()
        self.sessions[s.id] = s
        self.current_session_id = s.id
        self.messages = s.messages

    # ── Session management ──────────────────────────────────────────────

    def create_session(self, title: str = "New Session") -> Session:
        s = Session(title=title)
        self.sessions[s.id] = s
        self.switch_session(s.id)
        return s

    def switch_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.current_session_id = session_id
            self.messages = self.sessions[session_id].messages

    def close_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                remaining = list(self.sessions.keys())
                if remaining:
                    self.switch_session(remaining[-1])
                else:
                    self._init_default_session()

    # ── Messages ────────────────────────────────────────────────────────

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        if self.current_session_id and self.current_session_id in self.sessions:
            s = self.sessions[self.current_session_id]
            s.messages = self.messages
            s.updated_at = datetime.now()
            # Auto-title from first user message
            if message.role == "user" and s.title == "New Session":
                s.title = message.content[:40].strip()

    def clear_messages(self) -> None:
        self.messages.clear()
        if self.current_session_id and self.current_session_id in self.sessions:
            self.sessions[self.current_session_id].messages = self.messages

    # ── Agent state ──────────────────────────────────────────────────────

    def set_agent_status(self, status: AgentStatus, tool: str = "") -> None:
        self.agent_status = status
        self.current_tool = tool

    def add_thought(self, thought: str) -> None:
        self.thoughts_buffer.append(thought)

    def clear_thoughts(self) -> None:
        self.thoughts_buffer.clear()

    # ── Backend / LLM ───────────────────────────────────────────────────

    def set_backend_status(self, connected: bool, status: str = "") -> None:
        self.backend_connected = connected
        self.backend_status = status or ("connected" if connected else "offline")

    def set_active_model(self, model: str, provider: str = "") -> None:
        self.active_model = model
        self.active_provider = provider

    def add_token_usage(self, prompt: int, completion: int) -> None:
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += prompt + completion

    # ── Execution log ────────────────────────────────────────────────────

    def log_execution(self, type: str, content: str, source: str = "") -> None:
        self.execution_log.append({
            "type": type,
            "content": content,
            "source": source,
            "timestamp": datetime.now(),
        })

    def clear_execution_log(self) -> None:
        self.execution_log.clear()


# Global singleton
store = Store()