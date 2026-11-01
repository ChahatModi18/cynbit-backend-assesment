import enum
from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base


class InquiryStatusEnum(str, enum.Enum):
    """Lifecycle statuses for customer and partner inquiries."""
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    CONTACTED = "CONTACTED"
    RESOLVED = "RESOLVED"
    ARCHIVED = "ARCHIVED"


class Inquiry(Base):
    """
    Inquiry relational entity storing inquiries submitted via the public API.
    Replaces tight Next.js Server Action mutations with a normalized SQL table.
    """
    __tablename__ = "inquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[InquiryStatusEnum] = mapped_column(
        SQLEnum(InquiryStatusEnum),
        default=InquiryStatusEnum.PENDING,
        index=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationship to audit logs for full traceability
    audit_logs: Mapped[List["InquiryAuditLog"]] = relationship(
        "InquiryAuditLog",
        back_populates="inquiry",
        cascade="all, delete-orphan",
        order_by="desc(InquiryAuditLog.created_at)"
    )

    def __repr__(self) -> str:
        return f"<Inquiry id={self.id} email='{self.email}' status='{self.status}'>"


class InquiryAuditLog(Base):
    """
    Audit log record capturing every modification performed on an inquiry.
    Guarantees non-repudiation and traceability of administrative actions.
    """
    __tablename__ = "inquiry_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    inquiry_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inquiries.id", ondelete="CASCADE"),
        nullable=True
    )
    admin_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("admin_users.id", ondelete="SET NULL"),
        nullable=True
    )
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    old_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    inquiry: Mapped[Optional[Inquiry]] = relationship("Inquiry", back_populates="audit_logs")

