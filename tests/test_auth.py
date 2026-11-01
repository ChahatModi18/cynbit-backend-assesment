from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.models.admin import RoleEnum


def test_login_success_superadmin(client: TestClient):
    """Verify that a SuperAdmin can log in with valid credentials and receive a signed JWT."""
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "Admin@Cynbit2026!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 1800
    assert data["user"]["email"] == "admin@cynbit.in"
    assert data["user"]["role"] == "SUPER_ADMIN"


def test_login_success_reviewer(client: TestClient):
    """Verify that an Inquiry Reviewer can log in with valid credentials."""
    response = client.post("/api/v1/auth/login", json={
        "email": "reviewer@cynbit.in",
        "password": "Reviewer@Cynbit2026!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "reviewer@cynbit.in"
    assert data["user"]["role"] == "INQUIRY_REVIEWER"


def test_login_invalid_password(client: TestClient):
    """Verify that incorrect passwords return 401 Unauthorized with generic message."""
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "WrongPassword2026!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password."


def test_login_nonexistent_email(client: TestClient):
    """Verify that non-existent emails return identical 401 to prevent user enumeration."""
    response = client.post("/api/v1/auth/login", json={
        "email": "ghost.user@cynbit.in",
        "password": "SomePassword2026!"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password."


def test_login_malformed_email(client: TestClient):
    """Verify that malformed email inputs are rejected by Pydantic validation (422)."""
    response = client.post("/api/v1/auth/login", json={
        "email": "not-an-email",
        "password": "Admin@Cynbit2026!"
    })
    assert response.status_code == 422
    data = response.json()
    assert data["title"] == "Validation Error"


def test_login_short_password(client: TestClient):
    """Verify that passwords shorter than 8 characters fail schema validation."""
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "short"
    })
    assert response.status_code == 422


def test_get_current_admin_profile_success(client: TestClient, auth_headers_superadmin: dict):
    """Verify that an authenticated administrator can retrieve their profile via /auth/me."""
    response = client.get("/api/v1/auth/me", headers=auth_headers_superadmin)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@cynbit.in"
    assert data["role"] == "SUPER_ADMIN"
    assert data["is_active"] is True


def test_get_current_admin_profile_unauthorized(client: TestClient):
    """Verify that /auth/me rejects requests missing the Authorization header with 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    data = response.json()
    assert "Authentication required" in data["detail"]


def test_get_current_admin_profile_invalid_token(client: TestClient):
    """Verify that tampered or invalid JWTs are rejected with 401."""
    headers = {"Authorization": "Bearer this.is.not.a.valid.jwt.token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "Invalid, malformed, or untrusted" in data["detail"]


def test_get_current_admin_profile_expired_token(client: TestClient):
    """Verify that expired JWTs are rejected with a clear expiration detail."""
    expired_token = create_access_token(
        subject=1,
        role=RoleEnum.SUPER_ADMIN.value,
        email="admin@cynbit.in",
        expires_delta=timedelta(seconds=-1)
    )
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "expired" in data["detail"].lower()

