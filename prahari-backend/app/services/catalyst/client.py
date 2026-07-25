"""
Catalyst Services Layer — encapsulates all Zoho Catalyst API interactions.
"""

import httpx
from typing import Any, Dict, List, Optional
from loguru import logger
from app.config import get_settings

settings = get_settings()

CATALYST_BASE = "https://api.catalyst.zoho.com/baas/v1"


class CatalystAuthService:
    """Catalyst Authentication — user profile retrieval and token validation."""

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        url = f"https://{settings.CATALYST_AUTH_DOMAIN}/oauth/v2/userifo"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()


class CatalystCacheService:
    """Catalyst Cache — Redis-compatible key/value store for session caching."""

    def __init__(self, project_id: str, project_key: str):
        self.base_url = f"{CATALYST_BASE}/project/{project_id}/cache/{settings.CATALYST_CACHE_SEGMENT}"
        self.headers = {"CATALYST-PROJECT-KEY": project_key}

    async def get(self, key: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/{key}",
                headers=self.headers,
                timeout=5.0,
            )
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("cache_value")
            return None

    async def set(self, key: str, value: str, ttl_seconds: int = 3600) -> None:
        async with httpx.AsyncClient() as client:
            await client.post(
                self.base_url,
                json={"cache_name": key, "cache_value": value, "expiry_in_hours": ttl_seconds // 3600},
                headers=self.headers,
                timeout=5.0,
            )

    async def delete(self, key: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{self.base_url}/{key}",
                headers=self.headers,
                timeout=5.0,
            )


class CatalystStratusService:
    """Catalyst Stratus — file storage for media assets (FIR PDFs, images, CCTV)."""

    def __init__(self, project_id: str, project_key: str):
        self.base_url = f"{CATALYST_BASE}/project/{project_id}/storage"
        self.headers = {"CATALYST-PROJECT-KEY": project_key}
        self.bucket = settings.CATALYST_STRATUS_BUCKET

    async def get_upload_url(self, file_name: str, content_type: str) -> Dict[str, str]:
        """Get a pre-signed upload URL for direct browser upload."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/folder/{self.bucket}/file/upload",
                json={"file_name": file_name, "content_type": content_type},
                headers=self.headers,
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("data", {})

    async def get_download_url(self, file_id: str) -> str:
        """Get a signed download URL for a stored file."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/folder/{self.bucket}/file/{file_id}/download",
                headers=self.headers,
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json().get("data", {}).get("download_url", "")

    async def delete_file(self, file_id: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.delete(
                f"{self.base_url}/folder/{self.bucket}/file/{file_id}",
                headers=self.headers,
                timeout=10.0,
            )


class CatalystSignalsService:
    """Catalyst Signals — push notifications and real-time event broadcasting."""

    def __init__(self, project_id: str, project_key: str):
        self.base_url = f"{CATALYST_BASE}/project/{project_id}/signal"
        self.headers = {"CATALYST-PROJECT-KEY": project_key}

    async def publish(self, channel: str, event_type: str, payload: Dict[str, Any]) -> None:
        """Publish a real-time signal to a channel (e.g., 'alerts', 'case-updates')."""
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    f"{self.base_url}/channel/{channel}/publish",
                    json={"event_type": event_type, "payload": payload},
                    headers=self.headers,
                    timeout=5.0,
                )
            except httpx.HTTPError as e:
                logger.warning(f"Catalyst Signals publish failed: {e}")


# ── Singleton instances ───────────────────────────────────────────────────

def get_catalyst_auth() -> CatalystAuthService:
    return CatalystAuthService()


def get_catalyst_cache() -> CatalystCacheService:
    return CatalystCacheService(
        project_id=settings.CATALYST_PROJECT_ID,
        project_key=settings.CATALYST_PROJECT_KEY,
    )


def get_catalyst_stratus() -> CatalystStratusService:
    return CatalystStratusService(
        project_id=settings.CATALYST_PROJECT_ID,
        project_key=settings.CATALYST_PROJECT_KEY,
    )


def get_catalyst_signals() -> CatalystSignalsService:
    return CatalystSignalsService(
        project_id=settings.CATALYST_PROJECT_ID,
        project_key=settings.CATALYST_PROJECT_KEY,
    )
