"""
Role-Based Access Control (RBAC) for Prahari AI.
Defines all roles, permissions, and FastAPI permission dependency factories.
"""

from enum import Enum
from typing import List, Set
from fastapi import Depends
from app.core.exceptions import PermissionDeniedError
from app.core.auth import get_current_user
from app.db.postgres.models.user import UserRole


class Permission(str, Enum):
    # Case Management
    CASE_CREATE = "case:create"
    CASE_READ = "case:read"
    CASE_UPDATE = "case:update"
    CASE_DELETE = "case:delete"
    CASE_EXPORT = "case:export"

    # Investigation
    INVESTIGATION_MANAGE = "investigation:manage"
    INVESTIGATION_READ = "investigation:read"

    # Evidence
    EVIDENCE_CREATE = "evidence:create"
    EVIDENCE_READ = "evidence:read"
    EVIDENCE_UPDATE = "evidence:update"

    # Chargesheet & Court
    CHARGESHEET_FILE = "chargesheet:file"
    COURT_MANAGE = "court:manage"

    # Persons (Accused, Victims, Witnesses)
    PERSON_CREATE = "person:create"
    PERSON_READ = "person:read"
    PERSON_UPDATE = "person:update"

    # Intelligence / Analytics
    ANALYTICS_READ = "analytics:read"
    GRAPH_READ = "graph:read"
    AI_QUERY = "ai:query"
    PREDICTION_READ = "prediction:read"

    # Administration
    USER_MANAGE = "user:manage"
    STATION_MANAGE = "station:manage"
    AUDIT_READ = "audit:read"
    SYSTEM_CONFIG = "system:config"

    # Media
    MEDIA_UPLOAD = "media:upload"
    MEDIA_READ = "media:read"


# ── Role → Permission mapping ─────────────────────────────────────────────

ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: set(Permission),   # All permissions

    UserRole.SYS_ADMIN: {
        Permission.USER_MANAGE,
        Permission.STATION_MANAGE,
        Permission.AUDIT_READ,
        Permission.SYSTEM_CONFIG,
        Permission.CASE_READ,
        Permission.ANALYTICS_READ,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.MEDIA_READ,
    },

    UserRole.SCRB_ANALYST: {
        Permission.CASE_READ,
        Permission.CASE_EXPORT,
        Permission.ANALYTICS_READ,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.PREDICTION_READ,
        Permission.PERSON_READ,
        Permission.EVIDENCE_READ,
        Permission.INVESTIGATION_READ,
        Permission.MEDIA_READ,
    },

    UserRole.AI_ANALYST: {
        Permission.CASE_READ,
        Permission.ANALYTICS_READ,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.PREDICTION_READ,
        Permission.PERSON_READ,
        Permission.EVIDENCE_READ,
        Permission.MEDIA_READ,
    },

    UserRole.DIST_ADMIN: {
        Permission.CASE_READ,
        Permission.CASE_EXPORT,
        Permission.ANALYTICS_READ,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.PERSON_READ,
        Permission.EVIDENCE_READ,
        Permission.INVESTIGATION_READ,
        Permission.AUDIT_READ,
        Permission.MEDIA_READ,
    },

    UserRole.SHO: {
        Permission.CASE_CREATE,
        Permission.CASE_READ,
        Permission.CASE_UPDATE,
        Permission.CASE_EXPORT,
        Permission.INVESTIGATION_MANAGE,
        Permission.INVESTIGATION_READ,
        Permission.EVIDENCE_CREATE,
        Permission.EVIDENCE_READ,
        Permission.EVIDENCE_UPDATE,
        Permission.CHARGESHEET_FILE,
        Permission.COURT_MANAGE,
        Permission.PERSON_CREATE,
        Permission.PERSON_READ,
        Permission.PERSON_UPDATE,
        Permission.ANALYTICS_READ,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.MEDIA_UPLOAD,
        Permission.MEDIA_READ,
        Permission.AUDIT_READ,
    },

    UserRole.IO: {
        Permission.CASE_READ,
        Permission.CASE_UPDATE,
        Permission.INVESTIGATION_MANAGE,
        Permission.INVESTIGATION_READ,
        Permission.EVIDENCE_CREATE,
        Permission.EVIDENCE_READ,
        Permission.EVIDENCE_UPDATE,
        Permission.CHARGESHEET_FILE,
        Permission.PERSON_CREATE,
        Permission.PERSON_READ,
        Permission.PERSON_UPDATE,
        Permission.GRAPH_READ,
        Permission.AI_QUERY,
        Permission.MEDIA_UPLOAD,
        Permission.MEDIA_READ,
    },

    UserRole.DEO: {
        Permission.CASE_CREATE,
        Permission.CASE_READ,
        Permission.CASE_UPDATE,
        Permission.PERSON_CREATE,
        Permission.PERSON_READ,
        Permission.PERSON_UPDATE,
        Permission.EVIDENCE_CREATE,
        Permission.EVIDENCE_READ,
        Permission.MEDIA_UPLOAD,
        Permission.MEDIA_READ,
    },
}


def require_permissions(*permissions: Permission):
    """
    FastAPI dependency factory.
    Usage:
        @router.get("/cases", dependencies=[Depends(require_permissions(Permission.CASE_READ))])
    """

    async def _check(current_user=Depends(get_current_user)):
        user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
        for perm in permissions:
            if perm not in user_perms:
                raise PermissionDeniedError(
                    action=perm.value,
                    resource="this resource"
                )
        return current_user

    return Depends(_check)


def require_any_permission(*permissions: Permission):
    """Checks that the user has AT LEAST ONE of the listed permissions."""

    async def _check(current_user=Depends(get_current_user)):
        user_perms = ROLE_PERMISSIONS.get(current_user.role, set())
        if not any(perm in user_perms for perm in permissions):
            raise PermissionDeniedError(
                action=f"any of {[p.value for p in permissions]}",
                resource="this resource",
            )
        return current_user

    return Depends(_check)
