"""
Custom exception hierarchy for Prahari AI.
All domain errors should inherit from PrahariException.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException


class PrahariException(Exception):
    """Base exception for all Prahari AI business errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class NotFoundError(PrahariException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found.",
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "id": str(identifier)},
        )


class PermissionDeniedError(PrahariException):
    def __init__(self, action: str, resource: str):
        super().__init__(
            message=f"You do not have permission to {action} {resource}.",
            status_code=403,
            error_code="PERMISSION_DENIED",
            details={"action": action, "resource": resource},
        )


class AuthenticationError(PrahariException):
    def __init__(self, message: str = "Authentication required."):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_REQUIRED",
        )


class ValidationError(PrahariException):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {},
        )


class ConflictError(PrahariException):
    def __init__(self, resource: str, message: str):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details={"resource": resource},
        )


class WorkflowError(PrahariException):
    def __init__(self, workflow: str, step: str, message: str):
        super().__init__(
            message=message,
            status_code=400,
            error_code="WORKFLOW_ERROR",
            details={"workflow": workflow, "step": step},
        )


class DatabaseError(PrahariException):
    def __init__(self, message: str = "A database error occurred."):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
        )


class ExternalServiceError(PrahariException):
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"External service error ({service}): {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service},
        )
