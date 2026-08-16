"""WebSocket Chat Endpoint"""
import json
import uuid
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Session as SessionModel
from app.agents.graph import run_agent
from app.agents.schemas import ChatRequest, ProviderName
from app.auth.middleware import verify_ws_token

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_json(self, session_id: str, data: dict):
        ws = self.active_connections.get(session_id)
        if ws:
            await ws.send_json(data)

    async def send_text(self, session_id: str, text: str):
        ws = self.active_connections.get(session_id)
        if ws:
            await ws.send_text(text)


manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_chat(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None),
    token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for streaming chat"""
    # Verify authentication
    user_id = await verify_ws_token(token, db)
    if not user_id:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    # Generate session ID if not provided
    if not session_id:
        session_id = f"session_{uuid.uuid4().hex[:8]}"

    await manager.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "message":
                await handle_chat_message(websocket, session_id, user_id, message, db)
            elif message.get("type") == "interrupt":
                # Handle interrupt - stop current agent execution
                await websocket.send_json({"type": "interrupted"})
            elif message.get("type") == "confirm":
                # Handle confirmation response
                pass  # TODO: Implement confirmation handling
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "INTERNAL_ERROR",
            "message": str(e)
        })
        manager.disconnect(session_id)


async def handle_chat_message(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    message: dict,
    db: AsyncSession,
):
    """Process incoming chat message and stream response"""
    content = message.get("content", "")
    if not content.strip():
        return

    tools_allowed = message.get("tools", ["file", "browser", "shell"])
    model_preference = message.get("model", "auto")

    # Create chat request
    request = ChatRequest(
        message=content,
        session_id=session_id,
        model_preference=ProviderName(model_preference),
        tools_allowed=tools_allowed,
        stream=True,
    )

    # Stream agent response
    try:
        async for event in run_agent(request, user_id, stream=True):
            await websocket.send_json(event.model_dump(mode="json"))
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "code": "AGENT_ERROR",
            "message": str(e)
        })


@router.post("/chat")
async def chat_rest(
    request: ChatRequest,
    user_id: str = Depends(verify_ws_token),  # Reuse for now
    db: AsyncSession = Depends(get_db),
):
    """REST endpoint for non-streaming chat"""
    response = await run_agent(request, user_id, stream=False)
    return response