#!/usr/bin/env python3
"""
Local Development Setup Script
Run this once to initialize the database and create a default admin user.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import db_manager, init_sync_db
from app.db.database import User, Tier, ApiKey, Provider, UserPlugin
from app.config import settings
from sqlalchemy import select
import bcrypt


async def setup_local_dev():
    print("[SETUP] Setting up ELE Agent local development environment...")
    
    # Initialize database tables
    print("[DB] Creating database tables...")
    init_sync_db()
    await db_manager.init_db()
    print("[DB] Database initialized")
    
    async with db_manager.session() as db:
        # Check if admin user exists
        result = await db.execute(select(User).where(User.email == "admin@local.dev"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("[USER] Creating default admin user...")
            hashed_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
            admin = User(
                email="admin@local.dev",
                hashed_password=hashed_pw,
                full_name="Local Admin",
                tier=Tier.PRO,
                credits_daily=1000,
                is_active=True
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            print(f"[OK] Admin user created: admin@local.dev / admin123")
            print(f"   User ID: {admin.id}")
        else:
            print(f"[EXISTS] Admin user already exists: {admin.email}")
        
        # Create a free tier test user
        result = await db.execute(select(User).where(User.email == "user@local.dev"))
        test_user = result.scalar_one_or_none()
        
        if not test_user:
            print("[USER] Creating test user...")
            hashed_pw = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode()
            test_user = User(
                email="user@local.dev",
                hashed_password=hashed_pw,
                full_name="Test User",
                tier=Tier.FREE,
                credits_daily=100,
                is_active=True
            )
            db.add(test_user)
            await db.commit()
            await db.refresh(test_user)
            print(f"[OK] Test user created: user@local.dev / user123")
        else:
            print(f"[EXISTS] Test user already exists: {test_user.email}")
    
    await db_manager.close()
    print("\n[DONE] Local development setup complete!")
    print("\n[NEXT] Next steps:")
    print("   1. Copy .env.example to .env and add your API keys")
    print("   2. Start backend:  cd backend && .venv\\Scripts\\python -m uvicorn app.main:app --reload")
    print("   3. Start web:      cd web && npm run dev")
    print("   4. Start desktop:  cd desktop && npm run dev")
    print("\n[CREDS] Default credentials:")
    print("   Admin:  admin@local.dev / admin123  (PRO tier)")
    print("   User:   user@local.dev / user123    (FREE tier)")


if __name__ == "__main__":
    asyncio.run(setup_local_dev())