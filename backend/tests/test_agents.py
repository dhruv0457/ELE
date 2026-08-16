"""Test Agent Components"""
import pytest
from app.agents.schemas import (
    ProviderName, MessageRole, Message, ChatRequest, ChatResponse,
    ToolDeclaration, ThoughtEvent, ToolStartEvent, ToolResultEvent,
    FinalEvent, ErrorEvent, WSEvent
)


def test_provider_name_enum():
    """Test ProviderName enum values"""
    assert ProviderName.OPENAI == "openai"
    assert ProviderName.GEMINI == "gemini"
    assert ProviderName.OLLAMA == "ollama"
    assert ProviderName.OPENCLAW == "openclaw"
    assert ProviderName.ANTHROPIC == "anthropic"
    assert ProviderName.AUTO == "auto"


def test_message_role_enum():
    """Test MessageRole enum values"""
    assert MessageRole.SYSTEM == "system"
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    assert MessageRole.TOOL_RESULT == "tool_result"


def test_message_creation():
    """Test Message model creation"""
    msg = Message(role=MessageRole.USER, content="Hello")
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello"
    assert msg.name is None

    msg_with_name = Message(role=MessageRole.ASSISTANT, content="Hi", name="assistant")
    assert msg_with_name.name == "assistant"


def test_chat_request():
    """Test ChatRequest model"""
    req = ChatRequest(message="Test message")
    assert req.message == "Test message"
    assert req.interface == "web"
    assert req.model_preference == ProviderName.AUTO
    assert req.tools_allowed == ["file", "browser", "shell"]
    assert req.stream is False

    req_full = ChatRequest(
        message="Test",
        interface="cli",
        session_id="session-123",
        model_preference=ProviderName.OPENAI,
        tools_allowed=["file"],
        stream=True
    )
    assert req_full.interface == "cli"
    assert req_full.model_preference == ProviderName.OPENAI
    assert req_full.stream is True


def test_chat_response():
    """Test ChatResponse model"""
    resp = ChatResponse(
        session_id="session-123",
        response="Hello there!",
        thoughts=["Thinking...", "Done"],
        tools_used=["file"],
        duration_ms=100,
        model_used="gemini"
    )
    assert resp.session_id == "session-123"
    assert resp.response == "Hello there!"
    assert len(resp.thoughts) == 2
    assert "file" in resp.tools_used


def test_ws_events():
    """Test WebSocket event models"""
    thought = ThoughtEvent(content="Analyzing...", node="rag")
    assert thought.type == "thought"
    assert thought.content == "Analyzing..."

    tool_start = ToolStartEvent(tool="read_file", args={"path": "test.py"})
    assert tool_start.type == "tool_start"
    assert tool_start.tool == "read_file"

    tool_result = ToolResultEvent(tool="read_file", success=True, output="content")
    assert tool_result.type == "tool_result"
    assert tool_result.success is True

    final = FinalEvent(content="Done", session_id="sess-1", metadata={"model": "gemini"})
    assert final.type == "final"
    assert final.session_id == "sess-1"

    error = ErrorEvent(code="RATE_LIMITED", message="Too many requests", recoverable=True)
    assert error.type == "error"
    assert error.recoverable is True


def test_tool_declaration():
    """Test ToolDeclaration model"""
    tool = ToolDeclaration(
        name="read_file",
        description="Read a file",
        parameters={"type": "object", "properties": {"path": {"type": "string"}}}
    )
    assert tool.name == "read_file"
    assert "path" in tool.parameters["properties"]