"""Agent Schemas"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model_preference: str = "auto"
    tools_allowed: List[str] = Field(default_factory=lambda: ["file", "browser", "shell"])
    stream: bool = False


class ChatResponse(BaseModel):
    session_id: str
    response: str
    thoughts: List[str] = []
    screenshots: List[str] = []
    tools_used: List[str] = []
    duration_ms: int
    model_used: str


# WebSocket Event Types
class WSEvent(BaseModel):
    type: str


class ThoughtEvent(WSEvent):
    type: Literal["thought"] = "thought"
    content: str
    node: Optional[str] = None


class ToolStartEvent(WSEvent):
    type: Literal["tool_start"] = "tool_start"
    tool: str
    args: Dict[str, Any]


class ToolResultEvent(WSEvent):
    type: Literal["tool_result"] = "tool_result"
    tool: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None


class ScreenshotEvent(WSEvent):
    type: Literal["screenshot"] = "screenshot"
    data: str  # base64
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProgressEvent(WSEvent):
    type: Literal["progress"] = "progress"
    current: int
    total: int
    step: str


class FinalEvent(WSEvent):
    type: Literal["final"] = "final"
    content: str
    session_id: str
    metadata: Dict[str, Any] = {}


class ConfirmationEvent(WSEvent):
    type: Literal["confirmation_required"] = "confirmation_required"
    action_id: str
    action: str
    description: str
    risk_level: str


class ErrorEvent(WSEvent):
    type: Literal["error"] = "error"
    code: str
    message: str
    recoverable: bool = True


class PongEvent(WSEvent):
    type: Literal["pong"] = "pong"


# Union type for all WS events
AnyWSEvent = (
    ThoughtEvent | ToolStartEvent | ToolResultEvent |
    ScreenshotEvent | ProgressEvent | FinalEvent |
    ConfirmationEvent | ErrorEvent | PongEvent
)


# Provider Names
ProviderName = Literal["auto", "openai", "gemini", "groq", "nvidia", "claude", "ollama", "openclaw"]