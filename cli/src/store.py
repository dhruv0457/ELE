"""CLI Store - State Management"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ViewMode(str, Enum):
    CHAT = "chat"
    AUTONOMOUS = "autonomous"
    SETTINGS = "settings"
    PLUGINS = "plugins"
    TOOLS = "tools"


class OverlayStatus(str, Enum):
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    WORKING = "working"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass
class Message:
    id: str
    role: str  # user, assistant, system, tool
    content: str
    thoughts: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    is_streaming: bool = False


@dataclass
class Session:
    id: str
    title: str
    messages: List[Message] = field(default_factory=list)
    project: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PluginInfo:
    name: str
    version: str
    description: str
    enabled: bool = True
    permissions: List[str] = field(default_factory=list)


class Store:
    """Central state store for CLI"""

    def __init__(self):
        # Mode
        self.mode: ViewMode = ViewMode.CHAT
        self.previous_mode: ViewMode = ViewMode.CHAT

        # UI State
        self.sidebar_collapsed: bool = False
        self.sidebar_width: int = 240
        self.show_help: bool = False

        # Overlay
        self.overlay_visible: bool = False
        self.overlay_status: OverlayStatus = OverlayStatus.IDLE
        self.overlay_text: str = ""

        # Voice
        self.voice_enabled: bool = True
        self.voice_listening: bool = False

        # Sessions
        self.sessions: Dict[str, Session] = {}
        self.current_session_id: Optional[str] = None
        self.session_tabs: List[str] = []  # Ordered session IDs

        # Messages (for current session)
        self.messages: List[Message] = []

        # Autonomous mode state
        self.execution_stream: List[Dict[str, Any]] = []
        self.conversation_panel: List[Dict[str, Any]] = []
        self.ellie_state: OverlayStatus = OverlayStatus.IDLE

        # Plugins
        self.installed_plugins: List[PluginInfo] = []
        self.available_plugins: List[PluginInfo] = []

        # Settings
        self.settings: Dict[str, Any] = {}

        # Notifications
        self.notifications: List[Dict[str, Any]] = []

        # Connection
        self.backend_connected: bool = False
        self.backend_status: str = "disconnected"

        # Token usage
        self.token_usage: Dict[str, int] = {"prompt": 0, "completion": 0, "total": 0}

    # Mode management
    def set_mode(self, mode: ViewMode):
        self.previous_mode = self.mode
        self.mode = mode

    def toggle_mode(self):
        if self.mode == ViewMode.CHAT:
            self.set_mode(ViewMode.AUTONOMOUS)
        else:
            self.set_mode(ViewMode.CHAT)

    # Session management
    def create_session(self, title: str = "New Session") -> Session:
        import uuid
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = Session(id=session_id, title=title)
        self.sessions[session_id] = session
        self.session_tabs.append(session_id)
        self.switch_session(session_id)
        return session

    def switch_session(self, session_id: str):
        if session_id in self.sessions:
            self.current_session_id = session_id
            self.messages = self.sessions[session_id].messages

    def close_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            if session_id in self.session_tabs:
                self.session_tabs.remove(session_id)
            if self.current_session_id == session_id:
                if self.session_tabs:
                    self.switch_session(self.session_tabs[-1])
                else:
                    self.current_session_id = None
                    self.messages = []

    def add_message(self, message: Message):
        self.messages.append(message)
        if self.current_session_id:
            self.sessions[self.current_session_id].messages = self.messages
            self.sessions[self.current_session_id].updated_at = datetime.now()

    def update_message(self, message_id: str, **updates):
        for msg in self.messages:
            if msg.id == message_id:
                for key, value in updates.items():
                    setattr(msg, key, value)
                break

    # Autonomous mode
    def add_execution(self, entry: Dict[str, Any]):
        self.execution_stream.append(entry)

    def clear_execution(self):
        self.execution_stream.clear()

    def add_conversation(self, entry: Dict[str, Any]):
        self.conversation_panel.append(entry)

    def set_ellie_state(self, state: OverlayStatus):
        self.ellie_state = state
        self.overlay_status = state

    # Notifications
    def add_notification(self, title: str, message: str, level: str = "info"):
        self.notifications.append({
            "id": f"notif_{len(self.notifications)}",
            "title": title,
            "message": message,
            "level": level,
            "timestamp": datetime.now(),
        })

    def remove_notification(self, notif_id: str):
        self.notifications = [n for n in self.notifications if n["id"] != notif_id]

    # Backend connection
    def set_backend_status(self, connected: bool, status: str = ""):
        self.backend_connected = connected
        self.backend_status = status or ("connected" if connected else "disconnected")

    # Token usage
    def add_token_usage(self, prompt: int, completion: int):
        self.token_usage["prompt"] += prompt
        self.token_usage["completion"] += completion
        self.token_usage["total"] += prompt + completion


# Global store instance
store = Store()