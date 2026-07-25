"""
Application Configuration — Environment-based settings via pydantic-settings.
Integrates with Zoho Catalyst environment variables.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "Prahari AI"
    APP_ENV: str = "development"      # development | staging | production
    DEBUG: bool = False
    SECRET_KEY: str = "change-this-in-production"
    API_VERSION: str = "v1"

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://prahari-frontend.catalyst.zoho.com",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── PostgreSQL / PostGIS ───────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/prahari"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Neo4j AuraDB ──────────────────────────────────────────────────────
    NEO4J_URI: str = "neo4j+s://your-aura-instance.databases.neo4j.io"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "change-this"
    NEO4J_DATABASE: str = "neo4j"

    # ── Qdrant ────────────────────────────────────────────────────────────
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "prahari_cases"
    QDRANT_VECTOR_SIZE: int = 768

    # ── Zoho Catalyst ─────────────────────────────────────────────────────
    CATALYST_PROJECT_ID: str = ""
    CATALYST_PROJECT_KEY: str = ""
    CATALYST_ACCOUNT_ID: str = ""
    CATALYST_AUTH_DOMAIN: str = ""         # e.g. accounts.zoho.com
    CATALYST_STRATUS_BUCKET: str = "prahari-media"
    CATALYST_CACHE_SEGMENT: str = "prahari-cache"

    # ── Google Gemini (RAG / LLM) ─────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480      # 8 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Pagination ────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 25
    MAX_PAGE_SIZE: int = 200

    # ── AI Thresholds ─────────────────────────────────────────────────────
    RISK_SCORE_HIGH_THRESHOLD: float = 0.75
    RISK_SCORE_MEDIUM_THRESHOLD: float = 0.45
    ANOMALY_SENSITIVITY: float = 0.85


@lru_cache()
def get_settings() -> Settings:
    return Settings()
