"""Authentication Middleware"""
import jwt
from typing import Optional
from fastapi import Request, HTTPException, Depends, Cookie, WebSocket
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.db.database import get_db
from app.db.models import User


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health, docs, auth endpoints, and the WS chat (it does
        # its own token verification via verify_ws_token).
        public_paths = [
            "/health", "/docs", "/redoc", "/openapi.json",
            "/api/v1/login", "/api/v1/register", "/api/v1/logout",
            "/api/v1/ws/chat",
        ]
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)

        # Check for JWT in cookie
        token = request.cookies.get("access_token")
        if not token:
            # Check Authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return JSONResponse(
                status_code=401,
                content={"error": "AUTH_REQUIRED", "message": "Authentication required"}
            )

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            request.state.user_id = payload.get("sub")
            request.state.user_email = payload.get("email")
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"error": "TOKEN_EXPIRED", "message": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"error": "INVALID_TOKEN", "message": "Invalid token"}
            )

        return await call_next(request)


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


async def verify_ws_token(
    token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[str]:
    """Verify WebSocket token and return user_id"""
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    import time as _time
    payload = {
        "sub": user_id,
        "email": email,
        "exp": int(_time.time()) + (settings.JWT_EXPIRY_HOURS * 3600),
        "iat": int(_time.time()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)