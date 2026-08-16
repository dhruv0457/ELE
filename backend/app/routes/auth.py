"""Auth Routes"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.db.database import get_db
from app.db.models import User
from app.auth.middleware import create_access_token, get_current_user
from app.config.settings import settings

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Login with email/password"""
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user:
        # For MVP: auto-create user on first login
        import uuid
        user = User(
            id=str(uuid.uuid4()),
            email=request.email,
            tier="free",
            credits_remaining=settings.FREE_CREDITS_DAILY,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # TODO: Verify password hash (for now, accept any password)
    # In production: use bcrypt/argon2

    token = create_access_token(user.id, user.email)

    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.JWT_EXPIRY_HOURS * 3600,
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
    )


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register new user"""
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    import uuid
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        tier="free",
        credits_remaining=settings.FREE_CREDITS_DAILY,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(user.id, user.email)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=settings.JWT_EXPIRY_HOURS * 3600,
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": user.id,
        "email": user.email,
        "tier": user.tier,
        "credits_remaining": user.credits_remaining,
        "settings": user.settings,
    }