"""
Standardized API response wrapper for Prahari AI.
All endpoints return consistent envelope: { success, data, meta, error }
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    meta: Optional[PaginationMeta] = None

    @classmethod
    def ok(cls, data: T, message: Optional[str] = None) -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def paginated(
        cls,
        data: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "ApiResponse[List[T]]":
        total_pages = max(1, (total + page_size - 1) // page_size)
        return cls(
            success=True,
            data=data,
            meta=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
            ),
        )


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    details: Optional[dict] = None
