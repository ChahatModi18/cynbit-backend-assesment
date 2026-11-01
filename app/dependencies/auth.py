from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import AuthenticationException, PermissionDeniedException
from app.core.security import decode_access_token
from app.database.connection import get_db
from app.models.admin import AdminUser, RoleEnum

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login",
    auto_error=False
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Extract and cryptographically verify the JWT Bearer token from the Authorization header.
    Resolves the active AdminUser from the database.
    """
    if not token:
        raise AuthenticationException("Authentication required. Bearer token missing.")

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationException("Authentication token has expired. Please log in again.")
    except jwt.PyJWTError:
        raise AuthenticationException("Invalid, malformed, or untrusted authentication token.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Invalid token payload: missing subject identifier.")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthenticationException("Invalid token subject format.")

    stmt = select(AdminUser).where(AdminUser.id == user_id)
    user = db.scalar(stmt)

    if not user:
        raise AuthenticationException("Administrator account associated with token was not found.")

    if not user.is_active:
        raise PermissionDeniedException("This administrator account has been deactivated.")

    return user


def require_super_admin(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUser:
    """
    Role-Based Access Control (RBAC) guard.
    Restricts sensitive operations (e.g., inquiry deletion) exclusively to SUPER_ADMIN users.
    """
    if current_user.role != RoleEnum.SUPER_ADMIN:
        raise PermissionDeniedException(
            "Access forbidden: this action requires SUPER_ADMIN privilege."
        )
    return current_user

