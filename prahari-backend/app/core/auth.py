"""
Authentication core — JWT validation + Catalyst Auth token exchange.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from loguru import logger

from app.config import get_settings
from app.core.exceptions import AuthenticationError

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token."""
    return create_access_token(
        data, expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token. Raises AuthenticationError on failure."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid or expired token: {str(e)}")


async def verify_catalyst_token(catalyst_token: str) -> dict:
    """
    Exchange a Zoho Catalyst Auth token for user profile information.
    Called once during login to validate the Catalyst-issued token.
    """
    url = f"https://{settings.CATALYST_AUTH_DOMAIN}/oauth/v2/userifo"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                url,
                headers={"Authorization": f"Zoho-oauthtoken {catalyst_token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as e:
            logger.error(f"Catalyst Auth verification failed: {e}")
            raise AuthenticationError("Failed to verify Catalyst authentication token.")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    """
    FastAPI dependency — extracts and validates the Bearer JWT token.
    Returns the current user payload dict (user_id, role, station_id, district_id).
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationError("No authentication token provided.")

    payload = decode_token(credentials.credentials)

    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Token payload is missing user identifier.")

    # Lazy-import to avoid circular dependency
    from app.db.postgres.session import get_async_session
    from app.db.postgres.models.user import User
    from sqlalchemy import select

    # We attach minimal user context to the request
    # (in a production system, we'd use Redis cache here)
    return type("CurrentUser", (), {
        "id": user_id,
        "role": payload.get("role"),
        "station_id": payload.get("station_id"),
        "district_id": payload.get("district_id"),
        "email": payload.get("email"),
        "full_name": payload.get("full_name"),
        "payload": payload,
    })()
