from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.admin import RoleEnum


class LoginRequest(BaseModel):
    """Admin login request schema."""
    email: EmailStr = Field(
        ...,
        description="Registered administrator email address",
        examples=["admin@cynbit.in"]
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Account password (minimum 8 characters)",
        examples=["Admin@Cynbit2026!"]
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class AdminUserResponse(BaseModel):
    """Serialized public representation of an administrative account."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: RoleEnum
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime


class TokenResponse(BaseModel):
    """OAuth2 / JWT Token response payload."""
    access_token: str = Field(..., description="Signed JWT Bearer Access Token")
    token_type: str = Field("bearer", description="Token type indicator")
    expires_in: int = Field(..., description="Token validity window in seconds")
    user: AdminUserResponse = Field(..., description="Authenticated administrator details")


class AdminUserCreate(BaseModel):
    """Schema for provisioning a new administrator account."""
    email: EmailStr = Field(..., description="Administrator email address")
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    role: RoleEnum = Field(default=RoleEnum.INQUIRY_REVIEWER)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("full_name", mode="before")
    @classmethod
    def strip_name(cls, v: str) -> str:
        if isinstance(v, str):
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Full name cannot be empty.")
            return cleaned
        return v

