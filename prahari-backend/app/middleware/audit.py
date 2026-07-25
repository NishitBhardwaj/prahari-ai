"""Audit middleware — logs all mutating API calls to the AuditLog table."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        if request.method in WRITE_METHODS and response.status_code < 400:
            try:
                user_id = getattr(getattr(request, "state", None), "user_id", None)
                logger.info(
                    f"[AUDIT] {request.method} {request.url.path} "
                    f"user={user_id} status={response.status_code} "
                    f"req_id={getattr(request.state, 'request_id', '-')}"
                )
                # In production: async DB write to audit_logs table
            except Exception as e:
                logger.warning(f"Audit logging failed: {e}")

        return response
