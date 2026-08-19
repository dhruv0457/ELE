"""LangGraph Agent Orchestration - Fast, Single-Provider"""
import uuid
import json
import re
import asyncio
from typing import Dict, Any, List, AsyncGenerator, Optional, TypedDict
from datetime import datetime
import structlog

from langgraph.graph import StateGraph, END

from app.agents.schemas import (
    ProviderName, Message, ChatRequest, ChatResponse,
    ThoughtEvent, ToolStartEvent, ToolResultEvent,
    ProgressEvent, FinalEvent, WSEvent, ScreenshotEvent
)
from app.agents.llm_clients import get_orchestrator, orchestrator
from app.rag.indexer import RAGIndexer
from app.memory.manager import MemoryManager
from app.plugins.loader import PluginLoader
from app.executors.registry import ExecutorRegistry
from app.config.settings import settings

logger = structlog.get_logger()


class AgentState(TypedDict):
    messages: List[Message]
    session_id: str
    user_id: str
    model_preference: ProviderName
    tools_allowed: List[str]
    thoughts: List[str]
    screenshots: List[str]
    tools_used: List[str]
    rag_context: str
    current_tool: Optional[str]
    tool_results: List[Dict[str, Any]]
    error: Optional[str]
    llm_response: str
    final_response: str


async def input_node(state: AgentState) -> AgentState:
    logger.info("input_node", session_id=state["session_id"])
    state["thoughts"] = ["Received request"]
    return state


async def sanity_check_node(state: AgentState) -> AgentState:
    logger.info("sanity_check_node", session_id=state["session_id"])
    if not state["messages"]:
        state["error"] = "No messages provided"
    return state


async def llm_node(state: AgentState) -> AgentState:
    """Single provider LLM call - NVIDIA only for speed."""
    logger.info("llm_node", session_id=state["session_id"])

    # Use NVIDIA only (fastest single provider)
    preferred = state["model_preference"]
    if preferred != ProviderName.AUTO and preferred != ProviderName.NVIDIA:
        providers = [preferred] if settings.get_llm_provider_config(preferred) else ["nvidia"]
    else:
        providers = ["nvidia"]

    state["thoughts"].append("Querying NVIDIA LLM...")

    system_prompt = """You are ELE Agent, an AI assistant that controls the user's computer.
You have tools for file operations, shell commands, app launching, and browser automation.
Think step by step. Use tools when needed. Be concise and direct.
Output ONLY the final response or TOOL_CALL blocks.

BROWSER AUTOMATION TOOLS:
- browser_navigate: Navigate to a URL (e.g., "https://example.com")
- browser_click: Click an element by CSS selector
- browser_fill: Fill an input field by CSS selector
- browser_extract: Extract text or attribute from elements by CSS selector
- browser_screenshot: Take a screenshot (full_page optional)
- browser_eval_js: Execute JavaScript in the page context
- browser_wait: Wait for an element to appear by CSS selector
- browser_hover: Hover over an element
- browser_select: Select an option from a dropdown
- browser_back: Go back in browser history
- browser_forward: Go forward in browser history
- browser_reload: Reload the current page
- browser_get_content: Get full page HTML
- browser_get_text: Get visible page text
- browser_get_cookies: Get all cookies
- browser_set_cookies: Set cookies

BROWSER TOOL CALL FORMAT:
TOOL_CALL browser_navigate {"url": "https://example.com"}
TOOL_CALL browser_click {"selector": "button.submit"}
TOOL_CALL browser_fill {"selector": "input[name='email']", "value": "user@example.com"}
TOOL_CALL browser_extract {"selector": "h1"}
TOOL_CALL browser_screenshot {"full_page": true}
TOOL_CALL browser_eval_js {"script": "document.title"}
TOOL_CALL browser_wait {"selector": ".result", "timeout": 10000}

Use these tools when the user wants you to browse, click, fill forms, extract data, or automate web tasks."""

    rag_context = state.get("rag_context", "")
    if rag_context:
        system_prompt += f"\n\nContext:\n{rag_context}"

    messages = [
        {"role": "system", "content": system_prompt},
        *[m.model_dump() if hasattr(m, "model_dump") else m for m in state["messages"]]
    ]

    tools = []
    if "file" in state["tools_allowed"]:
        tools.extend([
            {"name": "read_file", "description": "Read file contents", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}},
            {"name": "write_file", "description": "Write file contents", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}},
            {"name": "list_files", "description": "List files in directory", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}},
        ])
    if "shell" in state["tools_allowed"]:
        tools.append({
            "name": "run_shell",
            "description": "Run shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "cmd": {"type": "string"},
                    "cwd": {"type": "string"}
                }
            }
        })
    if "app" in state["tools_allowed"]:
        tools.append({
            "name": "open_app",
            "description": "Launch application",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "args": {"type": "array", "items": {"type": "string"}}
                }
            }
        })
    if "browser" in state["tools_allowed"]:
        tools.extend([
            {
                "name": "browser_navigate",
                "description": "Navigate to a URL",
                "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}
            },
            {
                "name": "browser_click",
                "description": "Click an element by CSS selector",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}}
            },
            {
                "name": "browser_fill",
                "description": "Fill an input field",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}, "value": {"type": "string"}}}
            },
            {
                "name": "browser_extract",
                "description": "Extract text or attribute from elements",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}, "attribute": {"type": "string"}}}
            },
            {
                "name": "browser_screenshot",
                "description": "Take a screenshot",
                "parameters": {"type": "object", "properties": {"full_page": {"type": "boolean"}}}
            },
            {
                "name": "browser_eval_js",
                "description": "Execute JavaScript in page context",
                "parameters": {"type": "object", "properties": {"script": {"type": "string"}}}
            },
            {
                "name": "browser_wait",
                "description": "Wait for element to appear",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}, "timeout": {"type": "integer"}, "state": {"type": "string"}}}
            },
            {
                "name": "browser_hover",
                "description": "Hover over an element",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}}
            },
            {
                "name": "browser_select",
                "description": "Select option from dropdown",
                "parameters": {"type": "object", "properties": {"selector": {"type": "string"}, "value": {"type": "string"}}}
            },
            {
                "name": "browser_back",
                "description": "Go back in browser history",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_forward",
                "description": "Go forward in browser history",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_reload",
                "description": "Reload the current page",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_get_content",
                "description": "Get full page HTML",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_get_text",
                "description": "Get visible page text",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_get_cookies",
                "description": "Get all cookies",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "browser_set_cookies",
                "description": "Set cookies",
                "parameters": {"type": "object", "properties": {"cookies": {"type": "array", "items": {"type": "object"}}}}
            },
        ])
    
    # Desktop automation tools
    if "desktop" in state["tools_allowed"]:
        tools.extend([
            {
                "name": "move_mouse",
                "description": "Move mouse to coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "click",
                "description": "Click at coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "button": {"type": "string"}, "clicks": {"type": "integer"}}}
            },
            {
                "name": "double_click",
                "description": "Double click at coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "right_click",
                "description": "Right click at coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "drag",
                "description": "Drag from start to end coordinates",
                "parameters": {"type": "object", "properties": {"start_x": {"type": "integer"}, "start_y": {"type": "integer"}, "end_x": {"type": "integer"}, "end_y": {"type": "integer"}, "duration": {"type": "number"}}}
            },
            {
                "name": "type_text",
                "description": "Type text at current cursor position",
                "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "interval": {"type": "number"}}}
            },
            {
                "name": "press_key",
                "description": "Press a key",
                "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "presses": {"type": "integer"}, "interval": {"type": "number"}}}
            },
            {
                "name": "hotkey",
                "description": "Press key combination (e.g., ctrl+c)",
                "parameters": {"type": "object", "properties": {"keys": {"type": "array", "items": {"type": "string"}}}}
            },
            {
                "name": "scroll",
                "description": "Scroll mouse wheel",
                "parameters": {"type": "object", "properties": {"clicks": {"type": "integer"}, "x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "screenshot",
                "description": "Take a screenshot",
                "parameters": {"type": "object", "properties": {"full_page": {"type": "boolean"}}}
            },
            {
                "name": "screenshot_region",
                "description": "Take screenshot of a region",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}}}
            },
            {
                "name": "ocr",
                "description": "OCR text at screen coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "radius": {"type": "integer"}}}
            },
            {
                "name": "ocr_region",
                "description": "OCR text in a screen region",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}}}
            },
            {
                "name": "launch_app",
                "description": "Launch an application",
                "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}}}
            },
            {
                "name": "focus_window",
                "description": "Focus a window by title",
                "parameters": {"type": "object", "properties": {"title": {"type": "string"}}}
            },
            {
                "name": "close_window",
                "description": "Close a window by title",
                "parameters": {"type": "object", "properties": {"title": {"type": "string"}}}
            },
            {
                "name": "list_windows",
                "description": "List all open windows",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "get_window_info",
                "description": "Get window information",
                "parameters": {"type": "object", "properties": {"title": {"type": "string"}}}
            },
            {
                "name": "ocr_region",
                "description": "OCR text in a screen region",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}}}
            },
            {
                "name": "capture_region",
                "description": "Capture screen region",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "width": {"type": "integer"}, "height": {"type": "integer"}}}
            },
            {
                "name": "move_mouse",
                "description": "Move mouse to coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "click_at",
                "description": "Click at coordinates",
                "parameters": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}
            },
            {
                "name": "drag_drop",
                "description": "Drag from start to end coordinates",
                "parameters": {"type": "object", "properties": {"start_x": {"type": "integer"}, "start_y": {"type": "integer"}, "end_x": {"type": "integer"}, "end_y": {"type": "integer"}, "duration": {"type": "number"}}}
            },
        ])

    try:
        state["thoughts"].append("Querying NVIDIA LLM...")
        async for provider, chunk in orchestrator.stream_parallel(messages, providers, tools if tools else None):
            if provider not in state.get("llm_response", {}):
                state["llm_response"] = ""
            state["llm_response"] = state.get("llm_response", "") + chunk
    except Exception as e:
        logger.error("llm_error", error=str(e))
        state["llm_response"] = f"Error: {e}"

    state["thoughts"].append("LLM response received")
    return state


async def action_node(state: AgentState) -> AgentState:
    logger.info("action_node", session_id=state["session_id"])

    response = state.get("llm_response", "")
    if not response:
        state["thoughts"].append("No response to process")
        return state

    state["thoughts"].append("Executing tools...")

    executors = ExecutorRegistry()
    tool_results = []

    tool_patterns = {
        "read_file":          r'TOOL_CALL\s+read_file\s+(\{.*?\})',
        "write_file":         r'TOOL_CALL\s+write_file\s+(\{.*?\})',
        "list_files":         r'TOOL_CALL\s+list_files\s+(\{.*?\})',
        "run_shell":          r'TOOL_CALL\s+run_shell\s+(\{.*?\})',
        "open_app":           r'TOOL_CALL\s+open_app\s+(\{.*?\})',
        "browser_navigate":   r'TOOL_CALL\s+browser_navigate\s+(\{.*?\})',
        "browser_click":      r'TOOL_CALL\s+browser_click\s+(\{.*?\})',
        "browser_fill":       r'TOOL_CALL\s+browser_fill\s+(\{.*?\})',
        "browser_extract":    r'TOOL_CALL\s+browser_extract\s+(\{.*?\})',
        "browser_screenshot": r'TOOL_CALL\s+browser_screenshot\s+(\{.*?\})',
        "browser_eval_js":    r'TOOL_CALL\s+browser_eval_js\s+(\{.*?\})',
        "browser_wait":       r'TOOL_CALL\s+browser_wait\s+(\{.*?\})',
        "browser_hover":      r'TOOL_CALL\s+browser_hover\s+(\{.*?\})',
        "browser_select":     r'TOOL_CALL\s+browser_select\s+(\{.*?\})',
        # No-arg browser tools — match with optional empty braces or no braces
        "browser_back":       r'TOOL_CALL\s+browser_back(?:\s+\{\})?',
        "browser_forward":    r'TOOL_CALL\s+browser_forward(?:\s+\{\})?',
        "browser_reload":     r'TOOL_CALL\s+browser_reload(?:\s+\{\})?',
        "browser_get_content":r'TOOL_CALL\s+browser_get_content(?:\s+\{\})?',
        "browser_get_text":   r'TOOL_CALL\s+browser_get_text(?:\s+\{\})?',
        "browser_get_cookies":r'TOOL_CALL\s+browser_get_cookies(?:\s+\{\})?',
        "browser_set_cookies":r'TOOL_CALL\s+browser_set_cookies\s+(\{.*?\})',
        "move_mouse":         r'TOOL_CALL\s+move_mouse\s+(\{.*?\})',
        "click":              r'TOOL_CALL\s+click\s+(\{.*?\})',
        "click_at":           r'TOOL_CALL\s+click_at\s+(\{.*?\})',
        "double_click":       r'TOOL_CALL\s+double_click\s+(\{.*?\})',
        "right_click":        r'TOOL_CALL\s+right_click\s+(\{.*?\})',
        "drag":               r'TOOL_CALL\s+drag\s+(\{.*?\})',
        "drag_drop":          r'TOOL_CALL\s+drag_drop\s+(\{.*?\})',
        "type_text":          r'TOOL_CALL\s+type_text\s+(\{.*?\})',
        "press_key":          r'TOOL_CALL\s+press_key\s+(\{.*?\})',
        "hotkey":             r'TOOL_CALL\s+hotkey\s+(\{.*?\})',
        "scroll":             r'TOOL_CALL\s+scroll\s+(\{.*?\})',
        "screenshot":         r'TOOL_CALL\s+screenshot(?:\s+\{\})?',
        "screenshot_region":  r'TOOL_CALL\s+screenshot_region\s+(\{.*?\})',
        "ocr":                r'TOOL_CALL\s+ocr\s+(\{.*?\})',
        "ocr_region":         r'TOOL_CALL\s+ocr_region\s+(\{.*?\})',
        "capture_region":     r'TOOL_CALL\s+capture_region\s+(\{.*?\})',
        "launch_app":         r'TOOL_CALL\s+launch_app\s+(\{.*?\})',
        "focus_window":       r'TOOL_CALL\s+focus_window\s+(\{.*?\})',
        "close_window":       r'TOOL_CALL\s+close_window\s+(\{.*?\})',
        "list_windows":       r'TOOL_CALL\s+list_windows(?:\s+\{\})?',
        "get_window_info":    r'TOOL_CALL\s+get_window_info\s+(\{.*?\})',
    }

    # No-arg tools — these have no capture group so re.findall returns list of empty strings
    NO_ARG_TOOLS = {
        "browser_back", "browser_forward", "browser_reload",
        "browser_get_content", "browser_get_text", "browser_get_cookies",
        "screenshot", "list_windows",
    }

    for tool_name, pattern in tool_patterns.items():
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                # For no-arg tools, match is '' (empty capture or no group) → use {}
                if tool_name in NO_ARG_TOOLS or not match or match.strip() == '{}':
                    args = {}
                else:
                    args = json.loads(match)
                state["current_tool"] = tool_name
                state["thoughts"].append(f"Executing {tool_name}...")

                result = await executors.execute(tool_name, args, {
                    "session_id": state["session_id"],
                    "user_id": state["user_id"],
                    "working_dir": "~",
                })
                tool_results.append({"tool": tool_name, "success": True, "output": result})
                state["tools_used"].append(tool_name)
                state["thoughts"].append(f"{tool_name} completed")
            except Exception as e:
                logger.error("tool_execution_error", tool=tool_name, error=str(e))
                tool_results.append({"tool": tool_name, "success": False, "error": str(e)})

    state["tool_results"] = tool_results
    return state


async def response_node(state: AgentState) -> AgentState:
    logger.info("response_node", session_id=state["session_id"])

    # Extract final response (remove TOOL_CALL blocks)
    response = state.get("llm_response", "")
    # Remove TOOL_CALL blocks from final output
    clean_response = re.sub(r'TOOL_CALL\s+\w+\s+\{.*?\}', '', response, flags=re.DOTALL)
    clean_response = clean_response.strip()

    state["final_response"] = clean_response or "(no response)"
    state["thoughts"].append("Response ready")
    return state


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("input", input_node)
    workflow.add_node("sanity_check", sanity_check_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("action", action_node)
    workflow.add_node("response", response_node)

    workflow.set_entry_point("input")
    workflow.add_edge("input", "sanity_check")
    workflow.add_edge("sanity_check", "llm")
    workflow.add_edge("llm", "action")
    workflow.add_edge("action", "response")
    workflow.add_edge("response", END)

    return workflow.compile()


agent_graph = build_agent_graph()


async def run_agent(
    request: ChatRequest,
    user_id: str,
    stream: bool = False,
) -> ChatResponse | AsyncGenerator[WSEvent, None]:
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"

    initial_state = AgentState(
        messages=[Message(role="user", content=request.message)],
        session_id=session_id,
        user_id=user_id,
        model_preference=request.model_preference,
        tools_allowed=request.tools_allowed,
        thoughts=[],
        screenshots=[],
        tools_used=[],
        rag_context="",
        current_tool=None,
        tool_results=[],
        error=None,
        llm_response="",
        final_response="",
    )

    if stream:
        async def event_stream():
            async for event in _stream_agent_execution(initial_state):
                yield event
        return event_stream()
    else:
        final_state = await agent_graph.ainvoke(initial_state)
        return ChatResponse(
            session_id=session_id,
            response=final_state.get("final_response", ""),
            thoughts=final_state.get("thoughts", []),
            screenshots=final_state.get("screenshots", []),
            tools_used=final_state.get("tools_used", []),
            duration_ms=0,
            model_used="nvidia",
        )


async def _stream_agent_execution(state: AgentState) -> AsyncGenerator[WSEvent, None]:
    current_state = state

    yield ThoughtEvent(content="Received request", node="input")

    current_state = await sanity_check_node(current_state)
    if current_state.get("error"):
        yield ErrorEvent(code="NO_MESSAGES", message=current_state["error"])
        return

    current_state = await llm_node(current_state)
    for thought in current_state["thoughts"][-1:]:
        yield ThoughtEvent(content=thought, node="llm")

    current_state = await action_node(current_state)
    for tool_result in current_state.get("tool_results", []):
        yield ToolStartEvent(tool=tool_result["tool"], args={})
        if tool_result["success"]:
            yield ToolResultEvent(tool=tool_result["tool"], success=True, output=tool_result.get("output"))
        else:
            yield ToolResultEvent(tool=tool_result["tool"], success=False, error=tool_result.get("error"))

    current_state = await response_node(current_state)

    yield FinalEvent(
        content=current_state.get("final_response", ""),
        session_id=current_state["session_id"],
        metadata={
            "thoughts": current_state["thoughts"],
            "screenshots": current_state["screenshots"],
            "tools_used": current_state["tools_used"],
        }
    )