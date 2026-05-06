from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    success: bool = True
    message: str | None = None
    data: DataT


class PaginationMeta(BaseModel):
    page: int
    limit: int
    returned: int
    has_next: bool
    has_previous: bool


class PaginatedPayload(BaseModel, Generic[DataT]):
    items: list[DataT]
    pagination: PaginationMeta


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[Any] = Field(default_factory=list)
