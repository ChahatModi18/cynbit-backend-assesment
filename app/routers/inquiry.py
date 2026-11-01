from typing import Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import get_current_user, require_super_admin
from app.models.admin import AdminUser
from app.models.inquiry import InquiryStatusEnum
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.inquiry import (
    InquiryCreate,
    InquiryDetailResponse,
    InquiryResponse,
    InquiryStatusUpdate
)
from app.services.inquiry_service import InquiryService

router = APIRouter(prefix="/inquiries", tags=["Inquiry Management"])


@router.post(
    "",
    response_model=InquiryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Customer Inquiry",
    description="Public endpoint to submit a new inquiry. Replaces coupled Next.js Server Actions with a clean REST contract."
)
def create_inquiry(
    inquiry_data: InquiryCreate,
    db: Session = Depends(get_db)
) -> InquiryResponse:
    inquiry = InquiryService.create_inquiry(db=db, inquiry_data=inquiry_data)
    return InquiryResponse.model_validate(inquiry)


@router.get(
    "",
    response_model=PaginatedResponse[InquiryResponse],
    status_code=status.HTTP_200_OK,
    summary="List Inquiries (Admin)",
    description="Protected endpoint for administrators to list, filter, and search customer inquiries with pagination."
)
def list_inquiries(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    status_filter: Optional[InquiryStatusEnum] = Query(None, alias="status", description="Filter by inquiry status"),
    search: Optional[str] = Query(None, max_length=100, description="Keyword search across name, email, company, and subject"),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PaginatedResponse[InquiryResponse]:
    return InquiryService.list_inquiries(
        db=db,
        page=page,
        page_size=page_size,
        status=status_filter,
        search=search
    )


@router.get(
    "/{id}",
    response_model=InquiryDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Inquiry by ID (Admin)",
    description="Protected endpoint to retrieve full inquiry details along with complete historical audit logs."
)
def get_inquiry(
    id: int = Path(..., ge=1, description="Unique inquiry ID"),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> InquiryDetailResponse:
    inquiry = InquiryService.get_inquiry_by_id(db=db, inquiry_id=id)
    return InquiryDetailResponse.model_validate(inquiry)


@router.patch(
    "/{id}/status",
    response_model=InquiryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Inquiry Status (Admin)",
    description="Protected endpoint to transition an inquiry's status. Records an immutable audit log entry."
)
def update_inquiry_status(
    status_update: InquiryStatusUpdate,
    id: int = Path(..., ge=1, description="Unique inquiry ID"),
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> InquiryResponse:
    inquiry = InquiryService.update_inquiry_status(
        db=db,
        inquiry_id=id,
        status_update=status_update,
        current_user=current_user
    )
    return InquiryResponse.model_validate(inquiry)


@router.delete(
    "/{id}",
    response_model=SuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Inquiry (SuperAdmin Only)",
    description="Protected endpoint to delete an inquiry. Enforces Role-Based Access Control: restricted to SUPER_ADMIN."
)
def delete_inquiry(
    id: int = Path(..., ge=1, description="Unique inquiry ID"),
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    InquiryService.delete_inquiry(db=db, inquiry_id=id, current_user=current_user)
    return SuccessResponse(message=f"Inquiry {id} has been permanently deleted.")

