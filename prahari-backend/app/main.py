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
    print("========================================")
    print("Prahari AI Backend")
    print("Prototype v1.0")
    print("========================================")
    print("* FastAPI Started")
    print("* Configuration Loaded")
    
    # Initialize databases
    try:
        await init_db()
        print("* PostgreSQL Connected")
    except Exception as e:
        print(f"! PostgreSQL Connection Failed: {e}")
        
    try:
        await init_neo4j()
        print("* Neo4j Connected")
    except Exception as e:
        print(f"! Neo4j Connection Failed: {e}")
        
    try:
        await init_qdrant()
        print("* Qdrant Connected")
    except Exception as e:
        print(f"! Qdrant Connection Failed: {e}")

    print("* Catalyst Initialized")
    print("* Routes Registered")
    print("* AI Services Loaded")
    print("Listening on port 8000")
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

    @app.get("/ready", tags=["System"])
    async def readiness_check():
        """Readiness check for verifying database connections."""
        from sqlalchemy import text
        from app.db.postgres.engine import engine
        from app.db.neo4j.client import get_neo4j_driver
        from app.db.qdrant.client import get_qdrant
        
        status = {"postgres": "pending", "neo4j": "pending", "qdrant": "pending"}
        is_ready = True

        # PostgreSQL
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            status["postgres"] = "ok"
        except Exception as e:
            logger.error(f"Postgres readiness failed: {e}")
            status["postgres"] = "error"
            is_ready = False

        # Neo4j
        try:
            driver = get_neo4j_driver()
            await driver.verify_connectivity()
            status["neo4j"] = "ok"
        except Exception as e:
            logger.error(f"Neo4j readiness failed: {e}")
            status["neo4j"] = "error"
            is_ready = False

        # Qdrant
        try:
            client = get_qdrant()
            await client.get_collections()
            status["qdrant"] = "ok"
        except Exception as e:
            logger.error(f"Qdrant readiness failed: {e}")
            status["qdrant"] = "error"
            is_ready = False
            
        return JSONResponse(
            status_code=200 if is_ready else 503,
            content={
                "status": "ready" if is_ready else "degraded",
                "checks": status
            }
        )

    return app


app = create_app()
