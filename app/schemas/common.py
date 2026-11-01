from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata describing the pagination state of a query."""
    total_records: int = Field(..., description="Total count of matching records")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items returned per page")
    total_pages: int = Field(..., ge=0, description="Total number of available pages")
    has_next: bool = Field(..., description="True if a subsequent page exists")
    has_prev: bool = Field(..., description="True if a preceding page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated envelope wrapping a list of items with metadata."""
    items: List[T] = Field(..., description="List of records for the requested page")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


class SuccessResponse(BaseModel):
    """Standard generic success response envelope."""
    success: bool = True
    message: str = Field(..., description="Human-readable success message")

