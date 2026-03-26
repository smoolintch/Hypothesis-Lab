from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: str


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    error: None = None


class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    error: ErrorDetail
