from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.inquiry import InquiryStatusEnum


class InquiryCreate(BaseModel):
    """
    Validation schema for creating a new customer or business inquiry.
    Enforces server-side sanitization, whitespace rejection, and length bounds.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of inquirer",
        examples=["Rajesh Sharma"]
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Valid contact email address",
        examples=["rajesh.sharma@example.com"]
    )
    company: Optional[str] = Field(
        None,
        max_length=100,
        description="Organization or company name (optional)",
        examples=["Fintech Solutions India"]
    )
    subject: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Subject or domain of inquiry",
        examples=["AI Automation Architecture Consulting"]
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed inquiry text",
        examples=["We are exploring autonomous AI agents to automate our tier-1 support tickets."]
    )

    @field_validator("name", "subject", "message", mode="before")
    @classmethod
    def strip_and_validate_non_empty(cls, v: str) -> str:
        """Strip surrounding whitespace and reject empty/whitespace-only input."""
        if not isinstance(v, str):
            raise ValueError("Field must be a string.")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or contain only whitespace.")
        return cleaned

    @field_validator("company", mode="before")
    @classmethod
    def strip_company(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class InquiryStatusUpdate(BaseModel):
    """Schema for updating an inquiry's status by an administrator."""
    status: InquiryStatusEnum = Field(..., description="Target lifecycle status")
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Administrative notes explaining status transition",
        examples=["Spoke with client on discovery call; scheduled technical demo."]
    )

    @field_validator("notes", mode="before")
    @classmethod
    def strip_notes(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip()
        return cleaned if cleaned else None


class InquiryAuditLogResponse(BaseModel):
    """Audit log item response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    inquiry_id: Optional[int]
    admin_user_id: Optional[int]
    action: str
    old_status: Optional[str]
    new_status: Optional[str]
    notes: Optional[str]
    created_at: datetime


class InquiryResponse(BaseModel):
    """Public/Admin serialized inquiry representation."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    company: Optional[str]
    subject: str
    message: str
    status: InquiryStatusEnum
    created_at: datetime
    updated_at: datetime


class InquiryDetailResponse(InquiryResponse):
    """Detailed inquiry representation including historical audit logs."""
    audit_logs: List[InquiryAuditLogResponse] = []

