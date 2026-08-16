"""Voice Routes"""
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.middleware import get_current_user

router = APIRouter()


@router.post("/voice/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    user=Depends(get_current_user),
):
    """Convert speech to text"""
    # TODO: Implement STT
    return {"text": "", "engine": "whisper_api"}


@router.post("/voice/tts")
async def text_to_speech(
    text: str = Form(...),
    voice: str = Form("jarvis"),
    user=Depends(get_current_user),
):
    """Convert text to speech"""
    # TODO: Implement TTS
    return {"audio": b"", "engine": "edge"}


@router.get("/voice/voices")
async def list_voices(user=Depends(get_current_user)):
    """List available TTS voices"""
    return {
        "voices": [
            {"id": "jarvis", "name": "Jarvis (British Male)", "engine": "edge"},
            {"id": "female", "name": "Aria (US Female)", "engine": "edge"},
            {"id": "system", "name": "System Default", "engine": "pyttsx3"},
        ]
    }


@router.post("/voice/wake-word/toggle")
async def toggle_wake_word(
    enabled: bool = Form(...),
    user=Depends(get_current_user),
):
    """Enable/disable wake word detection"""
    return {"enabled": enabled}