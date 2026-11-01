import math
import logging
from typing import Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.core.exceptions import ResourceNotFoundException
from app.models.admin import AdminUser
from app.models.inquiry import Inquiry, InquiryAuditLog, InquiryStatusEnum
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.inquiry import (
    InquiryCreate,
    InquiryDetailResponse,
    InquiryResponse,
    InquiryStatusUpdate
)

logger = logging.getLogger("cynbit.inquiry_service")


class InquiryService:
    """Service handling inquiry creation, retrieval, status lifecycle, and deletion."""

    @staticmethod
    def create_inquiry(db: Session, inquiry_data: InquiryCreate) -> Inquiry:
        """
        Create a new customer inquiry with initial PENDING status and audit record.
        Replaces the coupled Next.js Server Action with an atomic transactional database write.
        """
        new_inquiry = Inquiry(
            name=inquiry_data.name,
            email=inquiry_data.email,
            company=inquiry_data.company,
            subject=inquiry_data.subject,
            message=inquiry_data.message,
            status=InquiryStatusEnum.PENDING,
        )
        db.add(new_inquiry)
        db.flush()  # Generate primary key ID

        # Record creation audit log
        audit_entry = InquiryAuditLog(
            inquiry_id=new_inquiry.id,
            admin_user_id=None,
            action="CREATED",
            old_status=None,
            new_status=InquiryStatusEnum.PENDING.value,
            notes="Inquiry submitted via public API"
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(new_inquiry)

        logger.info(f"New inquiry created: ID={new_inquiry.id}, Email='{new_inquiry.email}'")
        return new_inquiry

    @staticmethod
    def get_inquiry_by_id(db: Session, inquiry_id: int) -> Inquiry:
        """Retrieve an inquiry by its ID including related audit logs."""
        stmt = (
            select(Inquiry)
            .options(selectinload(Inquiry.audit_logs))
            .where(Inquiry.id == inquiry_id)
        )
        inquiry = db.scalar(stmt)

        if not inquiry:
            logger.warning(f"Inquiry lookup failed: ID={inquiry_id} does not exist.")
            raise ResourceNotFoundException(f"Inquiry with ID {inquiry_id} does not exist.")

        return inquiry

    @staticmethod
    def list_inquiries(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        status: Optional[InquiryStatusEnum] = None,
        search: Optional[str] = None
    ) -> PaginatedResponse[InquiryResponse]:
        """
        Retrieve a paginated list of inquiries with optional status filtering
        and case-insensitive keyword search across name, email, company, and subject.
        """
        stmt = select(Inquiry)

        # Status filter
        if status:
            stmt = stmt.where(Inquiry.status == status)

        # Keyword search filter
        if search:
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Inquiry.name.ilike(term),
                    Inquiry.email.ilike(term),
                    Inquiry.company.ilike(term),
                    Inquiry.subject.ilike(term)
                )
            )

        # Count total matching records
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_records = db.scalar(count_stmt) or 0

        # Calculate pagination bounds
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 0
        offset = (page - 1) * page_size

        # Fetch records sorted by most recent first
        query_stmt = (
            stmt
            .order_by(Inquiry.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        records = db.scalars(query_stmt).all()

        items = [InquiryResponse.model_validate(r) for r in records]

        pagination_meta = PaginationMeta(
            total_records=total_records,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )

        return PaginatedResponse[InquiryResponse](
            items=items,
            pagination=pagination_meta
        )

    @staticmethod
    def update_inquiry_status(
        db: Session,
        inquiry_id: int,
        status_update: InquiryStatusUpdate,
        current_user: AdminUser
    ) -> Inquiry:
        """
        Update the lifecycle status of an inquiry and record an immutable audit log entry.
        Guarantees full non-repudiation and accountability for administrative actions.
        """
        inquiry = InquiryService.get_inquiry_by_id(db, inquiry_id)
        old_status = inquiry.status.value
        new_status = status_update.status.value

        inquiry.status = status_update.status

        # Create audit trail entry
        audit_entry = InquiryAuditLog(
            inquiry_id=inquiry.id,
            admin_user_id=current_user.id,
            action="STATUS_UPDATED",
            old_status=old_status,
            new_status=new_status,
            notes=status_update.notes
        )
        db.add(audit_entry)
        db.commit()
        db.refresh(inquiry)

        logger.info(
            f"Inquiry ID={inquiry_id} status updated from '{old_status}' to '{new_status}' "
            f"by Admin='{current_user.email}' (ID={current_user.id})"
        )
        return inquiry

    @staticmethod
    def delete_inquiry(
        db: Session,
        inquiry_id: int,
        current_user: AdminUser
    ) -> bool:
        """
        Delete an inquiry permanently. Restricted to SUPER_ADMIN role.
        Related audit logs are removed via ON DELETE CASCADE.
        """
        inquiry = InquiryService.get_inquiry_by_id(db, inquiry_id)

        db.delete(inquiry)
        db.commit()

        logger.info(
            f"Inquiry ID={inquiry_id} permanently deleted by SuperAdmin='{current_user.email}' (ID={current_user.id})"
        )
        return True

