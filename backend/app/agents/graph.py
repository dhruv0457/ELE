"""LangGraph Agent Orchestration"""
import uuid
import json
import re
import asyncio
import aiosqlite
from typing import Dict, Any, List, AsyncGenerator, Optional, TypedDict
from datetime import datetime
import structlog

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.agents.schemas import (
    ProviderName, Message, ChatRequest, ChatResponse,
    ThoughtEvent, ToolStartEvent, ToolResultEvent,
    ScreenshotEvent, ProgressEvent, FinalEvent, WSEvent
)
from app.agents.llm_clients import get_orchestrator
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
    llm_responses: Dict[Any, str]
    merged_response: str
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


async def rag_node(state: AgentState) -> AgentState:
    logger.info("rag_node", session_id=state["session_id"])
    state["thoughts"].append("Retrieving relevant context...")
    try:
        rag = RAGIndexer()
        query = state["messages"][-1].content if isinstance(state["messages"][-1].content, str) else ""
        results = await rag.search(state["user_id"], query, k=5)
        state["rag_context"] = "\n\n".join([r["content"] for r in results])
        state["thoughts"].append(f"Found {len(results)} relevant documents")
    except Exception as e:
        logger.warning("rag_node_error", error=str(e))
        state["thoughts"].append("RAG retrieval failed")
    return state


async def llm_nodes_parallel(state: AgentState) -> AgentState:
    logger.info("llm_nodes_parallel", session_id=state["session_id"])

    available_providers = []
    for provider in ["gemini", "groq", "nvidia", "claude", "openai"]:
        if settings.get_llm_provider_config(provider) and settings.get_llm_provider_config(provider).enabled:
            available_providers.append(provider)
    available_providers.append("ollama")

    preferred = state["model_preference"]
    if preferred != ProviderName.AUTO and preferred in available_providers:
        providers = [preferred]
    else:
        providers = available_providers[:4]

    state["thoughts"].append(f"Querying {len(providers)} LLMs in parallel...")

    system_prompt = """You are ELE Agent, an AI assistant that can control the user's computer.
You have access to tools for file operations, browser automation, shell commands, and more.
Think step by step. Use tools when needed. Be concise but thorough."""

    rag_context = state.get("rag_context", "")
    if rag_context:
        system_prompt += f"\n\nRelevant context:\n{rag_context}"

    messages = [
        Message(role="system", content=system_prompt),
        *state["messages"]
    ]

    tools = []
    if "file" in state["tools_allowed"]:
        tools.extend([
            {"name": "read_file", "description": "Read file contents", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}},
            {"name": "write_file", "description": "Write file contents", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}}},
            {"name": "list_files", "description": "List files in directory", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}},
        ])
    if "browser" in state["tools_allowed"]:
        tools.extend([
            {"name": "browser_navigate", "description": "Navigate to URL", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}}},
            {"name": "browser_click", "description": "Click element", "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}}},
            {"name": "browser_extract", "description": "Extract text", "parameters": {"type": "object", "properties": {"selector": {"type": "string"}}}},
            {"name": "browser_screenshot", "description": "Take screenshot", "parameters": {"type": "object", "properties": {"full_page": {"type": "boolean"}}}},
        ])
    if "shell" in state["tools_allowed"]:
        tools.append({"name": "run_shell", "description": "Run shell command", "parameters": {"type": "object", "properties": {"cmd": {"type": "string"}, "cwd": {"type": "string"}}}})

    responses: Dict[ProviderName, str] = {}
    async for provider, chunk in orchestrator.stream_parallel(messages, providers, tools if tools else None):
        if provider not in responses:
            responses[provider] = ""
        responses[provider] += chunk

    state["thoughts"].append(f"Received responses from {len(responses)} providers")
    state["llm_responses"] = responses

    return state


async def merge_node(state: AgentState) -> AgentState:
    logger.info("merge_node", session_id=state["session_id"])
    state["thoughts"].append("Merging responses...")

    responses = state.get("llm_responses", {})
    if not responses:
        state["error"] = "No LLM responses received"
        return state

    merged = await orchestrator.merge_responses(responses)
    state["merged_response"] = merged
    state["thoughts"].append("Responses merged")
    return state


async def action_node(state: AgentState) -> AgentState:
    logger.info("action_node", session_id=state["session_id"])

    response = state.get("merged_response", "")
    if not response:
        state["thoughts"].append("No response to process")
        return state

    state["thoughts"].append("Executing tools...")

    executors = ExecutorRegistry()
    tool_results = []

    tool_patterns = {
        "read_file": r'TOOL_CALL\s+read_file\s+(\{.*?\})',
        "write_file": r'TOOL_CALL\s+write_file\s+(\{.*?\})',
        "list_files": r'TOOL_CALL\s+list_files\s+(\{.*?\})',
        "run_shell": r'TOOL_CALL\s+run_shell\s+(\{.*?\})',
        "browser_navigate": r'TOOL_CALL\s+browser_navigate\s+(\{.*?\})',
        "browser_click": r'TOOL_CALL\s+browser_click\s+(\{.*?\})',
        "browser_extract": r'TOOL_CALL\s+browser_extract\s+(\{.*?\})',
        "browser_screenshot": r'TOOL_CALL\s+browser_screenshot\s+(\{.*?\})',
    }

    for tool_name, pattern in tool_patterns.items():
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
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

                if tool_name == "browser_screenshot":
                    state["screenshots"].append(result)
            except Exception as e:
                logger.error("tool_execution_error", tool=tool_name, error=str(e))
                tool_results.append({"tool": tool_name, "success": False, "error": str(e)})

    state["tool_results"] = tool_results
    return state


async def response_node(state: AgentState) -> AgentState:
    logger.info("response_node", session_id=state["session_id"])

    response = state.get("merged_response", "")
    state["final_response"] = response
    state["thoughts"].append("Response ready")
    return state


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("input", input_node)
    workflow.add_node("sanity_check", sanity_check_node)
    workflow.add_node("rag", rag_node)
    workflow.add_node("llm_parallel", llm_nodes_parallel)
    workflow.add_node("merge", merge_node)
    workflow.add_node("action", action_node)
    workflow.add_node("response", response_node)

    workflow.set_entry_point("input")
    workflow.add_edge("input", "sanity_check")
    workflow.add_edge("sanity_check", "rag")
    workflow.add_edge("rag", "llm_parallel")
    workflow.add_edge("llm_parallel", "merge")
    workflow.add_edge("merge", "action")
    workflow.add_edge("action", "response")
    workflow.add_edge("response", END)

    # Use SQLite checkpointer for persistence (sync version for compile)
    import os
    db_path = os.path.expanduser("~/.ele-agent/checkpoints.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Use sync SqliteSaver for compilation, async will be used at runtime
    from langgraph.checkpoint.sqlite import SqliteSaver
    import sqlite3
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    return workflow.compile(checkpointer=checkpointer)


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
        llm_responses={},
        merged_response="",
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
            model_used="merged",
        )


async def _stream_agent_execution(state: AgentState) -> AsyncGenerator[WSEvent, None]:
    current_state = state

    yield ThoughtEvent(content="Received request", node="input")

    current_state = await sanity_check_node(current_state)
    if current_state.get("error"):
        yield ErrorEvent(code="NO_MESSAGES", message=current_state["error"])
        return

    current_state = await rag_node(current_state)
    for thought in current_state["thoughts"][-1:]:
        yield ThoughtEvent(content=thought, node="rag")

    current_state = await llm_nodes_parallel(current_state)
    for thought in current_state["thoughts"][-1:]:
        yield ThoughtEvent(content=thought, node="llm_parallel")

    current_state = await merge_node(current_state)
    for thought in current_state["thoughts"][-1:]:
        yield ThoughtEvent(content=thought, node="merge")

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