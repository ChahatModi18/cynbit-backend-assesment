"""
Pydantic Schemas Package — Request Validation & Response Models.
"""
from app.schemas.common import PaginationMeta, PaginatedResponse, SuccessResponse
from app.schemas.inquiry import (
    InquiryCreate,
    InquiryResponse,
    InquiryDetailResponse,
    InquiryStatusUpdate,
    InquiryAuditLogResponse
)
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    AdminUserResponse,
    AdminUserCreate
)

__all__ = [
    "PaginationMeta",
    "PaginatedResponse",
    "SuccessResponse",
    "InquiryCreate",
    "InquiryResponse",
    "InquiryDetailResponse",
    "InquiryStatusUpdate",
    "InquiryAuditLogResponse",
    "LoginRequest",
    "TokenResponse",
    "AdminUserResponse",
    "AdminUserCreate",
]

