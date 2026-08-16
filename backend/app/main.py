"""ELE Agent FastAPI Application"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.config.settings import settings
from app.db.database import db_manager, get_db
from app.routes import chat, plugins, voice, settings as settings_routes, telegram, health, auth
from app.auth.middleware import AuthMiddleware

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_ele_agent", version=settings.app.version)
    await db_manager.init_db()
    logger.info("database_initialized")
    yield
    await db_manager.close()
    logger.info("shutting_down_ele_agent")


app = FastAPI(
    title="ELE Agent API",
    version=settings.app.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", path=request.url.path, error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
    )


app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(plugins.router, prefix="/api/v1", tags=["plugins"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
app.include_router(settings_routes.router, prefix="/api/v1", tags=["settings"])
app.include_router(telegram.router, prefix="/api/v1", tags=["telegram"])


@app.get("/api/v1/db/status", tags=["database"])
async def db_status(db=Depends(get_db)):
    """Check database connectivity."""
    from sqlalchemy import text
    result = await db.execute(text("SELECT 1"))
    return {"status": "connected", "result": result.scalar()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)