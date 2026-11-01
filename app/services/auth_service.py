from datetime import datetime, timezone
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ConflictException
from app.core.security import create_access_token, hash_password, verify_password
from app.models.admin import AdminUser
from app.schemas.auth import AdminUserCreate, AdminUserResponse, TokenResponse

logger = logging.getLogger("cynbit.auth_service")


class AuthService:
    """Business logic for administrator authentication, identity management and token issuance."""

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> AdminUser:
        """
        Authenticate an administrator by email and plaintext password.
        Updates last_login_at timestamp on successful verification.
        """
        normalized_email = email.strip().lower()
        stmt = select(AdminUser).where(AdminUser.email == normalized_email)
        user = db.scalar(stmt)

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication attempt for email: {normalized_email}")
            raise AuthenticationException("Invalid email or password.")

        if not user.is_active:
            logger.warning(f"Authentication attempt for deactivated account: {normalized_email}")
            raise AuthenticationException("Administrator account has been deactivated.")

        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        logger.info(f"Successful authentication for user: {user.email} (ID: {user.id})")
        return user

    @staticmethod
    def create_admin_user(db: Session, user_data: AdminUserCreate) -> AdminUser:
        """Provision a new administrator with a unique email and bcrypt-hashed password."""
        normalized_email = user_data.email.strip().lower()
        stmt = select(AdminUser).where(AdminUser.email == normalized_email)
        existing = db.scalar(stmt)

        if existing:
            raise ConflictException(f"Administrator with email '{normalized_email}' already exists.")

        hashed_pw = hash_password(user_data.password)
        new_admin = AdminUser(
            email=normalized_email,
            full_name=user_data.full_name.strip(),
            hashed_password=hashed_pw,
            role=user_data.role,
            is_active=True
        )

        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        logger.info(f"Created new admin user: {new_admin.email} with role: {new_admin.role}")
        return new_admin

    @staticmethod
    def create_token_response(user: AdminUser) -> TokenResponse:
        """Construct the TokenResponse envelope containing signed JWT and user metadata."""
        token = create_access_token(
            subject=user.id,
            role=user.role.value,
            email=user.email
        )
        expires_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=expires_seconds,
            user=AdminUserResponse.model_validate(user)
        )

