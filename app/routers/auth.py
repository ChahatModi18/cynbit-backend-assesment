from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.dependencies.auth import get_current_user
from app.models.admin import AdminUser
from app.schemas.auth import AdminUserResponse, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Identity"])


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Administrator Login",
    description="Authenticates an administrator with email and password, issuing a signed JWT Bearer access token."
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    user = AuthService.authenticate_user(
        db=db,
        email=login_data.email,
        password=login_data.password
    )
    return AuthService.create_token_response(user)


@router.get(
    "/me",
    response_model=AdminUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current Administrator Profile",
    description="Retrieves the profile details and assigned role of the authenticated administrator."
)
def get_current_admin_profile(
    current_user: AdminUser = Depends(get_current_user)
) -> AdminUserResponse:
    return AdminUserResponse.model_validate(current_user)

