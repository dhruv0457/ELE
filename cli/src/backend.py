"""Backend client for the CLI - auth + WebSocket streaming chat."""
import asyncio
import json
import os
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional

import httpx
import websockets


def _state_dir() -> Path:
    base = os.environ.get("USERPROFILE") if os.name == "nt" else os.path.expanduser("~")
    p = Path(base) / ".ele-agent"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _token_path() -> Path:
    return _state_dir() / "token.json"


def save_token(access_token: str, user_id: str, email: str) -> None:
    _token_path().write_text(json.dumps({
        "access_token": access_token, "user_id": user_id, "email": email,
    }), encoding="utf-8")


def load_token() -> Optional[Dict[str, str]]:
    p = _token_path()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def clear_token() -> None:
    p = _token_path()
    if p.exists():
        p.unlink()


def backend_url(host: str = "localhost", port: int = 8000) -> str:
    return f"http://{host}:{port}"


def ws_url(host: str = "localhost", port: int = 8000) -> str:
    return f"ws://{host}:{port}"


def is_backend_up(host: str = "localhost", port: int = 8000, timeout: float = 2.0) -> bool:
    try:
        r = httpx.get(f"{backend_url(host, port)}/health", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def login_or_register(
    email: str = "ele@local.dev",
    password: str = "ele-agent",
    host: str = "localhost",
    port: int = 8000,
) -> Dict[str, str]:
    """Register (then login) returning a token. Caches it on disk."""
    cached = load_token()
    if cached and cached.get("access_token"):
        # Validate cached token against /me
        try:
            r = httpx.get(
                f"{backend_url(host, port)}/api/v1/me",
                headers={"Authorization": f"Bearer {cached['access_token']}"},
                timeout=5.0,
            )
            if r.status_code == 200:
                return cached
        except Exception:
            pass

    base = backend_url(host, port)
    # Use a real-domain email to satisfy EmailStr validation.
    real_email = email if "@" in email and not email.endswith(".local") else "ele@example.com"
    try:
        r = httpx.post(
            f"{base}/api/v1/login",
            json={"email": real_email, "password": password},
            timeout=10.0,
        )
        if r.status_code == 200:
            data = r.json()
        else:
            r = httpx.post(
                f"{base}/api/v1/register",
                json={"email": real_email, "password": password},
                timeout=10.0,
            )
            data = r.json()
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate with backend: {e}")

    save_token(data["access_token"], data["user_id"], data["email"])
    return {
        "access_token": data["access_token"],
        "user_id": data["user_id"],
        "email": data["email"],
    }


async def stream_chat(
    message: str,
    token: str,
    session_id: Optional[str] = None,
    tools: Optional[list] = None,
    model: str = "auto",
    host: str = "localhost",
    port: int = 8000,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Connect to the WS chat endpoint and yield parsed events until 'final'/'error'."""
    params = f"token={token}"
    if session_id:
        params += f"&session_id={session_id}"
    uri = f"{ws_url(host, port)}/api/v1/ws/chat?{params}"

    payload = {
        "type": "message",
        "content": message,
        "tools": tools or ["file", "shell", "browser"],
        "model": model,
    }

    try:
        async with websockets.connect(uri, max_size=None) as ws:
            await ws.send(json.dumps(payload))
            while True:
                try:
                    raw = await ws.recv()
                except websockets.ConnectionClosed:
                    break
                try:
                    evt = json.loads(raw)
                except Exception:
                    continue
                yield evt
                if evt.get("type") in ("final", "error"):
                    break
    except (websockets.exceptions.ConnectionRefusedError, OSError) as e:
        yield {"type": "error", "message": f"Connection failed: {e}"}


async def chat_once(
    message: str,
    token: str,
    session_id: Optional[str] = None,
    host: str = "localhost",
    port: int = 8000,
    timeout: float = 120.0,
) -> Dict[str, Any]:
    """Synchronous wrapper: send one message, accumulate events, return the final state."""
    final_content = ""
    thoughts = []
    tools_used = []
    async for evt in stream_chat(message, token, session_id=session_id, host=host, port=port):
        t = evt.get("type")
        if t == "thought":
            thoughts.append(evt.get("content", ""))
        elif t == "tool_start":
            tools_used.append(evt.get("tool", ""))
        elif t == "tool_result":
            pass
        elif t == "final":
            final_content = evt.get("content", "")
        elif t == "error":
            final_content = f"[error] {evt.get('message','unknown')}"
    return {
        "content": final_content,
        "thoughts": thoughts,
        "tools_used": tools_used,
        "session_id": session_id,
    }


async def async_is_backend_up(host: str = "localhost", port: int = 8000, timeout: float = 0.5) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{backend_url(host, port)}/health", timeout=timeout)
            return r.status_code == 200
    except Exception:
        return False


async def async_login_or_register(
    email: str = "ele@local.dev",
    password: str = "ele-agent",
    host: str = "localhost",
    port: int = 8000,
) -> Dict[str, str]:
    """Register (then login) returning a token. Caches it on disk."""
    cached = load_token()
    if cached and cached.get("access_token"):
        # Validate cached token against /me
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{backend_url(host, port)}/api/v1/me",
                    headers={"Authorization": f"Bearer {cached['access_token']}"},
                    timeout=3.0,
                )
                if r.status_code == 200:
                    return cached
        except Exception:
            pass

    base = backend_url(host, port)
    # Use a real-domain email to satisfy EmailStr validation.
    real_email = email if "@" in email and not email.endswith(".local") else "ele@example.com"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{base}/api/v1/login",
                json={"email": real_email, "password": password},
                timeout=3.0,
            )
            if r.status_code == 200:
                data = r.json()
            else:
                r = await client.post(
                    f"{base}/api/v1/register",
                    json={"email": real_email, "password": password},
                    timeout=3.0,
                )
                data = r.json()
    except Exception as e:
        raise RuntimeError(f"Failed to authenticate with backend: {e}")

    save_token(data["access_token"], data["user_id"], data["email"])
    return {
        "access_token": data["access_token"],
        "user_id": data["user_id"],
        "email": data["email"],
    }
