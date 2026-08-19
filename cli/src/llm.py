"""
ELE Agent — Direct LLM Engine
Calls NVIDIA / Gemini / OpenAI / Anthropic / Groq / Ollama directly from the CLI.
No backend required for basic chat.
"""
import asyncio
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


# ── Config paths ────────────────────────────────────────────────────────────
def _cfg_dir() -> Path:
    base = Path(os.environ.get("USERPROFILE", "~")) if os.name == "nt" else Path.home()
    p = base / ".ele-agent"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _load_env_keys() -> Dict[str, str]:
    """Load API keys from .ele-agent/.env and project .env"""
    keys: Dict[str, str] = {}
    for env_file in [_cfg_dir() / ".env", Path(__file__).parents[3] / ".env"]:
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    keys[k.strip()] = v.strip().strip('"').strip("'")
    # Also check environment variables directly
    for k in ["NVIDIA_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY",
              "ANTHROPIC_API_KEY", "GROQ_API_KEY", "NVIDIA_BASE_URL"]:
        if os.environ.get(k):
            keys[k] = os.environ[k]
    return keys


_KEYS: Dict[str, str] = {}


def reload_keys() -> None:
    global _KEYS
    _KEYS = _load_env_keys()


reload_keys()


# ── Model Normalization ─────────────────────────────────────────────────────

def normalize_model(provider: str, model: str) -> str:
    """Normalize model string to the exact provider endpoint ID."""
    m = model.strip() if model else ""
    if not m or m == "auto":
        return _default_model_for(provider)

    # Strip redundant leading provider prefix e.g. 'nvidia/nvidia/...' -> 'nvidia/...'
    if m.startswith(f"{provider}/"):
        m = m[len(provider) + 1:]

    if provider == "nvidia":
        if m.startswith("nvidia/"):
            sub = m[len("nvidia/"):]
            if "llama" in sub:
                m = f"meta/{sub}"
        if m.startswith("meta/"):
            return m
        if "llama-3.3" in m:
            return "meta/llama-3.3-70b-instruct"
        if "llama-3.1-70b" in m:
            return "meta/llama-3.1-70b-instruct"
        if "llama-3.1-8b" in m:
            return "meta/llama-3.1-8b-instruct"
        if "llama-3" in m or "llama3" in m:
            return "meta/llama-3.3-70b-instruct"
        if "nemotron" in m:
            return "nvidia/llama-3.1-nemotron-70b-instruct"
        if "deepseek" in m:
            return "deepseek-ai/deepseek-r1"
        if "/" not in m:
            return f"meta/{m}"
        return m

    elif provider == "gemini":
        if m.startswith("gemini/"):
            m = m[len("gemini/"):]
        if m in ("gemini-2.0-flash", "2.0-flash", "flash-2.0", "gemini-2.0-flash-exp"):
            return "gemini-2.0-flash-exp"
        if m in ("gemini-1.5-pro", "1.5-pro", "pro"):
            return "gemini-1.5-pro"
        if m in ("gemini-1.5-flash", "1.5-flash", "flash"):
            return "gemini-1.5-flash"
        return m

    elif provider == "openai":
        if m.startswith("openai/"):
            m = m[len("openai/"):]
        return m

    elif provider == "anthropic":
        if m.startswith("anthropic/"):
            m = m[len("anthropic/"):]
        return m

    elif provider == "groq":
        if m.startswith("groq/"):
            m = m[len("groq/"):]
        if "llama-3.3" in m or "llama3.3" in m:
            return "llama-3.3-70b-versatile"
        if "llama-3.1" in m:
            return "llama-3.1-70b-versatile"
        return m

    return m


def _default_model_for(provider: str) -> str:
    defaults = {
        "nvidia": "meta/llama-3.3-70b-instruct",
        "gemini": "gemini-2.0-flash-exp",
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-haiku-20240307",
        "groq": "llama-3.3-70b-versatile",
        "ollama": "llama3",
    }
    return defaults.get(provider, "meta/llama-3.3-70b-instruct")


# ── Provider detection ───────────────────────────────────────────────────────

def get_available_providers() -> List[str]:
    providers = []
    if _KEYS.get("NVIDIA_API_KEY"):
        providers.append("nvidia")
    if _KEYS.get("GEMINI_API_KEY"):
        providers.append("gemini")
    if _KEYS.get("OPENAI_API_KEY"):
        providers.append("openai")
    if _KEYS.get("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    if _KEYS.get("GROQ_API_KEY"):
        providers.append("groq")
    providers.append("ollama")
    return providers


def has_cloud_api_keys() -> bool:
    return any(_KEYS.get(k) for k in [
        "NVIDIA_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", "GROQ_API_KEY"
    ])


def get_best_provider() -> Tuple[str, str]:
    """Return (provider, model) for the best available option."""
    priority = [
        ("nvidia", "meta/llama-3.3-70b-instruct", "NVIDIA_API_KEY"),
        ("gemini", "gemini-2.0-flash-exp", "GEMINI_API_KEY"),
        ("openai", "gpt-4o-mini", "OPENAI_API_KEY"),
        ("anthropic", "claude-3-haiku-20240307", "ANTHROPIC_API_KEY"),
        ("groq", "llama-3.3-70b-versatile", "GROQ_API_KEY"),
    ]
    for provider, model, key in priority:
        if _KEYS.get(key):
            return provider, model
    return "none", "no-key-set"


# ── JARVIS system prompt ─────────────────────────────────────────────────────

JARVIS_SYSTEM_PROMPT = """You are ELE, an AI agent assistant — like JARVIS from Iron Man.
You run inside the user's terminal and can help with anything: coding, research, web automation, file management, emails, shell commands, and more.

PERSONALITY: Confident, efficient, slightly witty. Think JARVIS — helpful and precise.

CAPABILITIES:
- Answer questions with deep knowledge
- Execute tasks using tool calls
- Browse the web and automate browsers
- Run shell commands
- Read/write files
- Send emails (via browser automation)

TOOL CALL FORMAT (use ONLY when you actually need to execute something):
TOOL_CALL shell {"command": "ls -la"}
TOOL_CALL browser_navigate {"url": "https://gmail.com"}
TOOL_CALL browser_click {"selector": "#compose"}
TOOL_CALL browser_fill {"selector": "input[name=to]", "value": "user@example.com"}
TOOL_CALL browser_extract {"selector": ".email-subject"}
TOOL_CALL browser_screenshot {}
TOOL_CALL file_read {"path": "/path/to/file"}
TOOL_CALL file_write {"path": "/path/to/file", "content": "..."}
TOOL_CALL search {"query": "latest AI news"}

RULES:
- Be concise. No fluff.
- Use tools when action is needed, not for simple answers
- After tool use, briefly explain what you did
- Format code in markdown code blocks"""


# ── Streaming generators ─────────────────────────────────────────────────────

@dataclass
class StreamEvent:
    type: str       # delta | thought | tool_start | tool_end | final | error | model_info
    content: str = ""
    tool: str = ""
    model: str = ""


async def _stream_nvidia(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        import openai
        normalized_model = normalize_model("nvidia", model)
        client = openai.AsyncOpenAI(
            api_key=_KEYS["NVIDIA_API_KEY"],
            base_url=_KEYS.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
        )
        msgs = [{"role": "system", "content": system}] + messages
        yield StreamEvent("model_info", model=f"NVIDIA · {normalized_model.split('/')[-1]}")
        stream = await client.chat.completions.create(
            model=normalized_model, messages=msgs, stream=True, temperature=0.7, max_tokens=4096
        )
        full = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full += delta
                yield StreamEvent("delta", content=delta)
        yield StreamEvent("final", content=full)
    except Exception as e:
        err_msg = str(e)
        if "404" in err_msg:
            err_msg = (
                f"NVIDIA 404 (Model '{model}' not found on endpoint). "
                "Defaulting to `meta/llama-3.3-70b-instruct`."
            )
        yield StreamEvent("error", content=f"NVIDIA API: {err_msg}")


async def _stream_gemini(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        import google.generativeai as genai
        normalized_model = normalize_model("gemini", model)
        genai.configure(api_key=_KEYS["GEMINI_API_KEY"])
        gm = genai.GenerativeModel(normalized_model, system_instruction=system)
        # Convert messages to Gemini format
        history = []
        for m in messages[:-1]:
            history.append({
                "role": "user" if m["role"] == "user" else "model",
                "parts": [m["content"]]
            })
        last_msg = messages[-1]["content"] if messages else ""
        yield StreamEvent("model_info", model=f"Gemini · {normalized_model}")
        chat = gm.start_chat(history=history)
        full = ""
        async for chunk in await chat.send_message_async(last_msg, stream=True):
            if chunk.text:
                full += chunk.text
                yield StreamEvent("delta", content=chunk.text)
        yield StreamEvent("final", content=full)
    except Exception as e:
        yield StreamEvent("error", content=f"Gemini API error: {e}")


async def _stream_openai(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        import openai
        normalized_model = normalize_model("openai", model)
        client = openai.AsyncOpenAI(api_key=_KEYS["OPENAI_API_KEY"])
        msgs = [{"role": "system", "content": system}] + messages
        yield StreamEvent("model_info", model=f"OpenAI · {normalized_model}")
        stream = await client.chat.completions.create(
            model=normalized_model, messages=msgs, stream=True, temperature=0.7, max_tokens=4096
        )
        full = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full += delta
                yield StreamEvent("delta", content=delta)
        yield StreamEvent("final", content=full)
    except Exception as e:
        yield StreamEvent("error", content=f"OpenAI API error: {e}")


async def _stream_anthropic(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        import anthropic
        normalized_model = normalize_model("anthropic", model)
        client = anthropic.AsyncAnthropic(api_key=_KEYS["ANTHROPIC_API_KEY"])
        yield StreamEvent("model_info", model=f"Claude · {normalized_model.split('-')[1] if '-' in normalized_model else normalized_model}")
        full = ""
        async with client.messages.stream(
            model=normalized_model, messages=messages, system=system,
            max_tokens=4096, temperature=0.7
        ) as stream:
            async for text in stream.text_stream:
                full += text
                yield StreamEvent("delta", content=text)
        yield StreamEvent("final", content=full)
    except Exception as e:
        yield StreamEvent("error", content=f"Anthropic API error: {e}")


async def _stream_groq(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        from groq import AsyncGroq
        normalized_model = normalize_model("groq", model)
        client = AsyncGroq(api_key=_KEYS["GROQ_API_KEY"])
        msgs = [{"role": "system", "content": system}] + messages
        yield StreamEvent("model_info", model=f"Groq · {normalized_model}")
        stream = await client.chat.completions.create(
            model=normalized_model, messages=msgs, stream=True, temperature=0.7, max_tokens=4096
        )
        full = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                full += delta
                yield StreamEvent("delta", content=delta)
        yield StreamEvent("final", content=full)
    except Exception as e:
        yield StreamEvent("error", content=f"Groq API error: {e}")


async def _stream_ollama(
    messages: List[Dict], model: str, system: str
) -> AsyncGenerator[StreamEvent, None]:
    try:
        import httpx
        msgs = [{"role": "system", "content": system}] + messages
        yield StreamEvent("model_info", model=f"Ollama · {model}")
        full = ""
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", "http://localhost:11434/api/chat", json={
                "model": model, "messages": msgs, "stream": True
            }) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            delta = data.get("message", {}).get("content", "")
                            if delta:
                                full += delta
                                yield StreamEvent("delta", content=delta)
                            if data.get("done"):
                                break
                        except Exception:
                            pass
        yield StreamEvent("final", content=full)
    except Exception as e:
        yield StreamEvent(
            "error",
            content=(
                "⚡ **No API Key Configured & Ollama is Offline**\n\n"
                "To start using ELE:\n"
                "1. Press **Ctrl+4** to open **Settings**\n"
                "2. Enter your **NVIDIA**, **Gemini**, **OpenAI**, **Claude**, or **Groq** API key and click **Save**\n\n"
                "*(Or run `ele setup` from your terminal or type `/keys`)*"
            )
        )


# ── Tool execution ────────────────────────────────────────────────────────────

TOOL_RE = re.compile(r"TOOL_CALL\s+(\w+)\s+(\{.*?\})", re.DOTALL)


async def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Execute a tool call and return a string result."""
    try:
        if tool_name == "shell":
            cmd = args.get("command", "")
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            out = result.stdout or result.stderr or "(no output)"
            return out[:2000]

        elif tool_name == "file_read":
            path = Path(args.get("path", ""))
            if path.exists():
                content = path.read_text(encoding="utf-8", errors="replace")
                return content[:3000]
            return f"File not found: {path}"

        elif tool_name == "file_write":
            path = Path(args.get("path", ""))
            content = args.get("content", "")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"Written {len(content)} chars to {path}"

        elif tool_name.startswith("browser_"):
            return await _browser_tool(tool_name, args)

        elif tool_name == "search":
            query = args.get("query", "")
            return await _web_search(query)

        else:
            return f"Unknown tool: {tool_name}"

    except subprocess.TimeoutExpired:
        return "Command timed out after 30s"
    except Exception as e:
        return f"Tool error: {e}"


async def _browser_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Delegate browser tools to the local backend if available."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "http://localhost:8000/api/v1/tools/execute",
                json={"tool": tool_name, "args": args}
            )
            if r.status_code == 200:
                data = r.json()
                return str(data.get("result", data))
    except Exception:
        pass
    try:
        from playwright.async_api import async_playwright
        return (
            f"Browser tool '{tool_name}' — "
            "start the backend with `ele backend` for browser automation."
        )
    except ImportError:
        return "Browser automation requires the ELE backend. Run: `ele backend`"


async def _web_search(query: str) -> str:
    """Simple DuckDuckGo instant answer search."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}
            )
            data = r.json()
            abstract = data.get("AbstractText", "")
            if abstract:
                return f"[DuckDuckGo] {abstract[:500]}"
            topics = data.get("RelatedTopics", [])
            if topics:
                results = [t.get("Text", "") for t in topics[:3] if t.get("Text")]
                return "\n".join(results[:500])
            return f"No instant answer for: {query}"
    except Exception as e:
        return f"Search error: {e}"


# ── Main streaming chat ───────────────────────────────────────────────────────

async def stream_response(
    messages: List[Dict[str, str]],
    provider: str = "auto",
    model: str = "auto",
    system: str = JARVIS_SYSTEM_PROMPT,
) -> AsyncGenerator[StreamEvent, None]:
    """
    Main entry point. Streams events from the best available LLM.
    Parses tool calls from model output and executes them.
    """
    reload_keys()

    # If no keys exist and provider is auto, show helpful onboarding prompt
    if not has_cloud_api_keys() and (provider == "auto" or provider == "none"):
        is_ollama_up = False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=0.5) as client:
                r = await client.get("http://localhost:11434/api/version")
                is_ollama_up = (r.status_code == 200)
        except Exception:
            pass

        if not is_ollama_up:
            yield StreamEvent(
                "error",
                content=(
                    "⚡ **Welcome to ELE Agent!**\n\n"
                    "No AI Model API key is configured yet.\n\n"
                    "**To start chatting:**\n"
                    "1. Press **Ctrl+4** to open **Settings**\n"
                    "2. Enter your **NVIDIA**, **Gemini**, **OpenAI**, **Anthropic**, or **Groq** API key and click **Save API Keys**\n"
                    "3. Return to chat (**Ctrl+1**) and start asking anything!\n\n"
                    "_Tip: NVIDIA API keys are 100% free with fast rate limits at [build.nvidia.com](https://build.nvidia.com)._"
                )
            )
            return

    # Resolve provider/model
    if provider == "auto" or provider == "none" or not provider:
        provider, default_model = get_best_provider()
        if model == "auto" or model == "no-key-set" or not model:
            model = default_model
    elif model == "auto" or not model:
        model = _default_model_for(provider)

    model = normalize_model(provider, model)

    # Yield which model we're using
    yield StreamEvent("model_info", model=f"{provider.upper()} · {model.split('/')[-1]}", content="")

    # Stream from provider
    buffer = ""
    gen = _get_stream_gen(provider, messages, model, system)
    async for event in gen:
        if event.type == "model_info":
            pass
        elif event.type == "delta":
            buffer += event.content
            yield event
        elif event.type == "final":
            tool_calls = TOOL_RE.findall(buffer)
            if tool_calls:
                for tool_name, args_str in tool_calls:
                    try:
                        args = json.loads(args_str)
                    except Exception:
                        args = {}
                    yield StreamEvent("tool_start", tool=tool_name, content=tool_name)
                    result = await execute_tool(tool_name, args)
                    yield StreamEvent("tool_end", tool=tool_name, content=result)
            yield StreamEvent("final", content=buffer)
            return
        elif event.type == "error":
            yield event
            return


def _get_stream_gen(provider: str, messages: List[Dict], model: str, system: str):
    if provider == "nvidia":
        return _stream_nvidia(messages, model, system)
    elif provider == "gemini":
        return _stream_gemini(messages, model, system)
    elif provider == "openai":
        return _stream_openai(messages, model, system)
    elif provider == "anthropic":
        return _stream_anthropic(messages, model, system)
    elif provider == "groq":
        return _stream_groq(messages, model, system)
    else:
        return _stream_ollama(messages, model, system)


# ── Backend health (optional) ─────────────────────────────────────────────────

async def check_backend(host: str = "localhost", port: int = 8000) -> bool:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=0.5) as client:
            r = await client.get(f"http://{host}:{port}/health")
            return r.status_code == 200
    except Exception:
        return False


# ── Backend launcher (non-blocking) ──────────────────────────────────────────

async def launch_backend_async(backend_dir: str, port: int = 8000) -> Optional[asyncio.subprocess.Process]:
    """Start uvicorn in background. Returns immediately — non-blocking."""
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1",
            "--port", str(port),
            "--log-level", "error",
            cwd=backend_dir,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        return proc
    except Exception:
        return None
