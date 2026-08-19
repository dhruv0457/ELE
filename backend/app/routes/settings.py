"""Settings Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.middleware import get_current_user
from app.config.settings import settings, NVIDIA_NIM_MODELS

router = APIRouter()


@router.get("/settings")
async def get_settings(user=Depends(get_current_user)):
    """Get user settings"""
    return {
        "theme": "tokyo-night",
        "language": "en",
        "auto_update": True,
        "telemetry": "errors",
    }


@router.patch("/settings")
async def update_settings(
    new_settings: dict,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings"""
    # TODO: Implement settings update
    return {"message": "Settings updated"}


@router.get("/settings/api-keys")
async def list_api_keys(user=Depends(get_current_user)):
    """List configured API keys (masked)"""
    return {
        "providers": {
            "nvidia":    {"configured": bool(settings.NVIDIA_API_KEY),    "model": "meta/llama-3.1-8b-instruct"},
            "gemini":    {"configured": bool(settings.GEMINI_API_KEY),    "model": "gemini-2.0-flash-exp"},
            "groq":      {"configured": bool(settings.GROQ_API_KEY),      "model": "llama-3.3-70b-versatile"},
            "claude":    {"configured": bool(settings.ANTHROPIC_API_KEY), "model": "claude-3-haiku-20240307"},
            "openai":    {"configured": bool(settings.OPENAI_API_KEY),    "model": "gpt-4o-mini"},
        }
    }


@router.get("/settings/providers")
async def list_providers(user=Depends(get_current_user)):
    """List all available providers and their supported models"""
    return {
        "providers": {
            "nvidia": {
                "name": "NVIDIA NIM",
                "configured": bool(settings.NVIDIA_API_KEY),
                "base_url": "https://integrate.api.nvidia.com/v1",
                "models": NVIDIA_NIM_MODELS,
                "default": "meta/llama-3.1-8b-instruct",
                "hint": "Get a free API key at build.nvidia.com",
            },
            "gemini": {
                "name": "Google Gemini",
                "configured": bool(settings.GEMINI_API_KEY),
                "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                "default": "gemini-2.0-flash-exp",
                "hint": "Get a free API key at aistudio.google.com",
            },
            "groq": {
                "name": "Groq (Ultra Fast)",
                "configured": bool(settings.GROQ_API_KEY),
                "models": [
                    "llama-3.3-70b-versatile", "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768", "gemma2-9b-it",
                ],
                "default": "llama-3.3-70b-versatile",
                "hint": "Get a free API key at console.groq.com/keys",
            },
            "openai": {
                "name": "OpenAI",
                "configured": bool(settings.OPENAI_API_KEY),
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "o1-mini"],
                "default": "gpt-4o-mini",
                "hint": "Get an API key at platform.openai.com",
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "configured": bool(settings.ANTHROPIC_API_KEY),
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
                "default": "claude-3-haiku-20240307",
                "hint": "Get an API key at console.anthropic.com",
            },
        }
    }


@router.post("/settings/api-keys")
async def add_api_key(
    provider: str,
    key: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add/update API key for provider"""
    # TODO: Encrypt and store key
    return {"message": f"API key for {provider} saved"}


@router.delete("/settings/api-keys/{provider}")
async def remove_api_key(
    provider: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove API key for provider"""
    return {"message": f"API key for {provider} removed"}