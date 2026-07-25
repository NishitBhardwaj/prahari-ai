"""
Prahari AI Backend — FastAPI Application Factory
Karnataka State Police | Crime Intelligence Platform
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import get_settings
from app.core.exceptions import PrahariException
from app.db.postgres.engine import init_db, close_db
from app.db.neo4j.client import init_neo4j, close_neo4j
from app.db.qdrant.client import init_qdrant
from app.api.v1.router import api_router
from app.middleware.audit import AuditMiddleware
from app.middleware.request_id import RequestIDMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle manager."""
    logger.info("Prahari AI backend starting up...")

    # Initialize databases
    await init_db()
    await init_neo4j()
    await init_qdrant()

    logger.info("All database connections established.")
    yield

    # Shutdown
    logger.info("Prahari AI backend shutting down...")
    await close_db()
    await close_neo4j()
    logger.info("Connections closed. Goodbye.")


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI application."""

    app = FastAPI(
        title="Prahari AI — Crime Intelligence Platform",
        description=(
            "Enterprise-grade AI-powered Crime Intelligence and Case Management Platform "
            "for the Karnataka State Police. Integrates predictive analytics, graph intelligence, "
            "geospatial mapping, and natural language investigation capabilities."
        ),
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "Karnataka Police — Prahari AI Team",
            "email": "prahari-ai@ksp.gov.in",
        },
    )

    # ── Middleware ─────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(AuditMiddleware)

    # ── Routers ────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Global exception handler ───────────────────────────────────────────
    @app.exception_handler(PrahariException)
    async def prahari_exception_handler(request: Request, exc: PrahariException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.get("/health", tags=["System"])
    async def health_check():
        """Health check endpoint for AppSail monitoring."""
        return {
            "status": "healthy",
            "service": "prahari-backend",
            "version": "1.0.0",
        }

    return app


app = create_app()
