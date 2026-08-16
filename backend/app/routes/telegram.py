"""Telegram Routes"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.middleware import get_current_user

router = APIRouter()


@router.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Telegram webhook endpoint"""
    # TODO: Implement webhook handling
    return {"status": "ok"}


@router.get("/telegram/status")
async def telegram_status(user=Depends(get_current_user)):
    """Get Telegram bot status"""
    return {
        "connected": False,
        "username": None,
    }


@router.post("/telegram/send")
async def telegram_send(
    message: str,
    user=Depends(get_current_user),
):
    """Send message via Telegram bot (admin only)"""
    return {"message": "Sent"}