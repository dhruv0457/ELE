"""Database Manager with Async SQLAlchemy"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.config.settings import settings
from app.db.models import Base


class DatabaseManager:
    def __init__(self):
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def initialize(self, database_url: Optional[str] = None) -> None:
        """Initialize the database engine and session factory"""
        url = database_url or settings.DATABASE_URL
        # Expand tilde in path
        if url.startswith("sqlite"):
            url = url.replace("~", os.path.expanduser("~"))
        
        self.engine = create_async_engine(
            url,
            echo=settings.DEBUG,
            poolclass=NullPool if "sqlite" in url else None,
            connect_args={"check_same_thread": False} if "sqlite" in url else {},
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init_db(self) -> None:
        """Create all tables"""
        if not self.engine:
            self.initialize()
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        """Close the database engine"""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.session_factory = None

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session"""
        if not self.session_factory:
            self.initialize()
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def execute_raw(self, query: str, params: dict = None) -> any:
        """Execute raw SQL query"""
        async with self.session() as session:
            result = await session.execute(text(query), params or {})
            return result


# Global database manager
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session"""
    async with db_manager.session() as session:
        yield session