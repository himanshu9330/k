"""
SentinelAI-X Common API Schemas
=================================
Defines standard success and error response wrappers for all endpoints.
"""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiErrorDetail(BaseModel):
    code: str = Field(description="Machine-readable error identifier")
    message: str = Field(description="Human-readable error explanation")
    details: Optional[Any] = Field(default=None, description="Optional extra error context")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ApiErrorDetail


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
