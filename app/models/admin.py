import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class RoleEnum(str, enum.Enum):
    """Administrator roles for Role-Based Access Control (RBAC)."""
    SUPER_ADMIN = "SUPER_ADMIN"
    INQUIRY_REVIEWER = "INQUIRY_REVIEWER"


class AdminUser(Base):
    """
    Administrator user model supporting individual identity, bcrypt credentials,
    and role segregation (directly mitigating FIND-001 single-shared key risk).
    """
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(
        SQLEnum(RoleEnum),
        default=RoleEnum.INQUIRY_REVIEWER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<AdminUser id={self.id} email='{self.email}' role='{self.role}'>"

