"""
CognitiveOS API — Application Entry Point

An Operating Layer Between Human Cognition and Artificial Intelligence
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import make_asgi_app

from src.config.settings import get_settings
from src.config.logging import configure_logging
from src.database.connection import init_db, close_db
from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.routes import cognitive, sessions, feedback, health

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown."""
    configure_logging()
    logger.info("CognitiveOS API starting", version=settings.API_VERSION, env=settings.ENV)

    await init_db()
    logger.info("Database connection pool initialized")

    yield  # Application running

    await close_db()
    logger.info("CognitiveOS API shut down cleanly")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CognitiveOS API",
        description="Cognitive Processing Pipeline — Intent, Mode, Ambiguity, Vocabulary, Structure, Synthesis",
        version=settings.API_VERSION,
        docs_url="/api/docs" if settings.ENV != "production" else None,
        redoc_url="/api/redoc" if settings.ENV != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────
    prefix = f"/api/{settings.API_VERSION}"
    app.include_router(health.router, prefix=prefix, tags=["health"])
    app.include_router(cognitive.router, prefix=prefix, tags=["cognitive"])
    app.include_router(sessions.router, prefix=prefix, tags=["sessions"])
    app.include_router(feedback.router, prefix=prefix, tags=["feedback"])

    # ── Prometheus metrics ─────────────────────────────────────
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENV == "development",
        log_level="info",
    )
