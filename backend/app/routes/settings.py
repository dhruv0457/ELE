"""Settings Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.middleware import get_current_user
from app.config.settings import settings

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
            "gemini": {"configured": False, "model": "gemini-1.5-pro"},
            "groq": {"configured": False, "model": "llama-3.1-70b-versatile"},
            "nvidia": {"configured": False, "model": "nemotron-3-ultra"},
            "claude": {"configured": False, "model": "claude-3-5-sonnet"},
            "openai": {"configured": False, "model": "gpt-4o"},
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