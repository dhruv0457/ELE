"""Plugins Routes"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.auth.middleware import get_current_user

router = APIRouter()


@router.get("/plugins")
async def list_plugins(user=Depends(get_current_user)):
    """List installed plugins"""
    return {"plugins": []}


@router.get("/plugins/marketplace")
async def browse_marketplace(
    category: str = None,
    sort: str = "trending",
    user=Depends(get_current_user),
):
    """Browse plugin marketplace"""
    return {"plugins": []}


@router.post("/plugins/install")
async def install_plugin(
    name: str,
    version: str = "latest",
    user=Depends(get_current_user),
):
    """Install plugin from marketplace"""
    return {"message": f"Installing {name}@{version}"}


@router.delete("/plugins/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    user=Depends(get_current_user),
):
    """Uninstall plugin"""
    return {"message": f"Plugin {plugin_id} uninstalled"}


@router.post("/plugins/{plugin_id}/enable")
async def enable_plugin(
    plugin_id: str,
    user=Depends(get_current_user),
):
    """Enable plugin"""
    return {"message": f"Plugin {plugin_id} enabled"}


@router.post("/plugins/{plugin_id}/disable")
async def disable_plugin(
    plugin_id: str,
    user=Depends(get_current_user),
):
    """Disable plugin"""
    return {"message": f"Plugin {plugin_id} disabled"}