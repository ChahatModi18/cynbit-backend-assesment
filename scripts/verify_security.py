import os
import sys
from datetime import datetime, timedelta, timezone

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.database.connection import SessionLocal
from app.main import app
from app.models.admin import AdminUser, RoleEnum
from app.models.inquiry import Inquiry, InquiryStatusEnum


def run_security_verification():
    print("=" * 80)
    print("CYNBIT TECHNOLOGIES — SECURITY & AUTHENTICATION INTEGRATION VERIFICATION")
    print("=" * 80)
    
    # ---------------- 1. PASSWORD HASHING VERIFICATION ----------------
    print("\n[TEST 1] Password Hashing & Non-Plaintext Storage (Bcrypt)")
    test_password = "SuperSecretPassword123!"
    hashed = hash_password(test_password)
    print(f"  Plaintext: '{test_password}'")
    print(f"  Bcrypt Hash (starts with): {hashed[:29]}...")
    assert hashed != test_password, "FAIL: Password was not hashed!"
    assert hashed.startswith("$2b$12$"), f"FAIL: Expected bcrypt cost factor 12 prefix, got {hashed[:7]}"
    assert verify_password(test_password, hashed) is True, "FAIL: Valid password failed verification!"
    assert verify_password("WrongPassword!", hashed) is False, "FAIL: Invalid password verified successfully!"
    print("  [PASS] Bcrypt password hashing and verification working correctly (Cost factor 12).")

    # ---------------- 2. DATABASE CREDENTIAL INSPECTION ----------------
    print("\n[TEST 2] Database Credential Inspection (No Plaintext Passwords)")
    db = SessionLocal()
    try:
        users = db.scalars(select(AdminUser)).all()
        for u in users:
            print(f"  User: {u.email} | Role: {u.role.value} | Hash: {u.hashed_password[:20]}...")
            assert u.hashed_password.startswith("$2b$12$"), f"FAIL: User {u.email} does not have a bcrypt hash!"
            assert "Password" not in u.hashed_password, "FAIL: Plaintext found in password field!"
        print(f"  [PASS] All {len(users)} registered users have secure bcrypt hashes in database.")
    finally:
        db.close()

    # ---------------- 3. JWT TOKEN CREATION & CLAIMS ----------------
    print("\n[TEST 3] JWT Token Generation & Claims Verification")
    token = create_access_token(
        subject=1,
        role=RoleEnum.SUPER_ADMIN.value,
        email="admin@cynbit.in",
        expires_delta=timedelta(minutes=30)
    )
    print(f"  Generated JWT: {token[:35]}...")
    claims = decode_access_token(token)
    print(f"  Decoded Claims: sub={claims['sub']}, role={claims['role']}, email={claims['email']}, exp={claims['exp']}")
    assert claims["sub"] == "1", f"FAIL: Expected sub '1', got {claims['sub']}"
    assert claims["role"] == RoleEnum.SUPER_ADMIN.value, f"FAIL: Expected role {RoleEnum.SUPER_ADMIN.value}"
    assert claims["iss"] == "cynbit-auth-service", "FAIL: Missing or invalid issuer tag"
    print("  [PASS] JWT claims validated successfully.")

    # ---------------- 4. EXPIRED JWT REJECTION ----------------
    print("\n[TEST 4] Expired JWT Token Handling")
    expired_token = create_access_token(
        subject=1,
        role=RoleEnum.SUPER_ADMIN.value,
        email="admin@cynbit.in",
        expires_delta=timedelta(seconds=-10)  # Expired in past
    )
    try:
        decode_access_token(expired_token)
        raise AssertionError("FAIL: Expired token did not raise ExpiredSignatureError!")
    except jwt.ExpiredSignatureError:
        print("  [PASS] Expired JWT correctly raises ExpiredSignatureError.")

    # ---------------- 5. TAMPERED JWT REJECTION ----------------
    print("\n[TEST 5] Tampered / Malformed JWT Handling")
    tampered_token = token[:-5] + "XXXXX"  # Corrupt cryptographic signature
    try:
        decode_access_token(tampered_token)
        raise AssertionError("FAIL: Tampered token did not raise PyJWTError!")
    except jwt.PyJWTError:
        print("  [PASS] Tampered signature correctly rejected by PyJWT.")

    # ---------------- 6. ENDPOINT AUTHENTICATION VIA TESTCLIENT ----------------
    print("\n[TEST 6] Endpoint Authentication via TestClient")
    client = TestClient(app)

    # 6a. Missing Token
    res_unauth = client.get("/api/v1/auth/me")
    print(f"  GET /api/v1/auth/me without token -> Status {res_unauth.status_code}")
    assert res_unauth.status_code == 401, f"FAIL: Expected 401, got {res_unauth.status_code}"
    assert res_unauth.json()["title"] == "Authentication Failed"
    print("  [PASS] Missing token correctly rejected with 401 Unauthorized.")

    # 6b. Expired Token on Protected Endpoint
    res_exp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    print(f"  GET /api/v1/auth/me with expired token -> Status {res_exp.status_code}")
    assert res_exp.status_code == 401, f"FAIL: Expected 401, got {res_exp.status_code}"
    assert "expired" in res_exp.json()["detail"].lower()
    print("  [PASS] Expired token on protected route rejected with 401 and descriptive message.")

    # 6c. Invalid Credentials on Login
    res_bad_login = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "WrongPassword2026!"
    })
    print(f"  POST /api/v1/auth/login with wrong password -> Status {res_bad_login.status_code}")
    assert res_bad_login.status_code == 401
    assert res_bad_login.json()["detail"] == "Invalid email or password."
    print("  [PASS] Wrong password rejected with 401 (generic message prevents user enumeration).")

    # 6d. Successful SuperAdmin Login
    res_admin_login = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "Admin@Cynbit2026!"
    })
    print(f"  POST /api/v1/auth/login SuperAdmin -> Status {res_admin_login.status_code}")
    assert res_admin_login.status_code == 200
    admin_token = res_admin_login.json()["access_token"]
    assert res_admin_login.json()["user"]["role"] == "SUPER_ADMIN"
    print("  [PASS] SuperAdmin login succeeded; JWT issued.")

    # 6e. Successful Reviewer Login
    res_rev_login = client.post("/api/v1/auth/login", json={
        "email": "reviewer@cynbit.in",
        "password": "Reviewer@Cynbit2026!"
    })
    print(f"  POST /api/v1/auth/login Reviewer -> Status {res_rev_login.status_code}")
    assert res_rev_login.status_code == 200
    rev_token = res_rev_login.json()["access_token"]
    assert res_rev_login.json()["user"]["role"] == "INQUIRY_REVIEWER"
    print("  [PASS] Reviewer login succeeded; JWT issued with INQUIRY_REVIEWER role.")

    # ---------------- 7. ROLE-BASED ACCESS CONTROL (RBAC) ----------------
    print("\n[TEST 7] Role-Based Access Control (RBAC) Verification")
    
    # Create test inquiry to test deletion
    res_new = client.post("/api/v1/inquiries", json={
        "name": "RBAC Test Contact",
        "email": "rbac@example.com",
        "subject": "RBAC Test Subject",
        "message": "Testing role based authorization on deletion."
    })
    test_inq_id = res_new.json()["id"]
    print(f"  Created test inquiry ID={test_inq_id}")

    # Reviewer attempts DELETE -> Should be 403 Forbidden
    res_forbidden = client.delete(
        f"/api/v1/inquiries/{test_inq_id}",
        headers={"Authorization": f"Bearer {rev_token}"}
    )
    print(f"  DELETE by INQUIRY_REVIEWER -> Status {res_forbidden.status_code}")
    assert res_forbidden.status_code == 403, f"FAIL: Expected 403 Forbidden, got {res_forbidden.status_code}"
    assert "SUPER_ADMIN" in res_forbidden.json()["detail"]
    print("  [PASS] INQUIRY_REVIEWER is strictly forbidden from deleting inquiries (403 Forbidden).")

    # SuperAdmin attempts DELETE -> Should be 200 OK
    res_deleted = client.delete(
        f"/api/v1/inquiries/{test_inq_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    print(f"  DELETE by SUPER_ADMIN -> Status {res_deleted.status_code}")
    assert res_deleted.status_code == 200
    assert res_deleted.json()["success"] is True
    print("  [PASS] SUPER_ADMIN authorized to delete inquiries (200 OK).")

    # ---------------- 8. SECURITY HEADERS VERIFICATION ----------------
    print("\n[TEST 8] Security Headers & Banner Suppression (FIND-004 to FIND-007)")
    res_h = client.get("/api/v1/health")
    headers = res_h.headers
    print(f"  X-Frame-Options: {headers.get('x-frame-options')}")
    print(f"  X-Content-Type-Options: {headers.get('x-content-type-options')}")
    print(f"  Content-Security-Policy: {headers.get('content-security-policy')}")
    print(f"  Strict-Transport-Security: {headers.get('strict-transport-security')}")
    print(f"  Server header present: {'server' in headers}")
    print(f"  X-Powered-By header present: {'x-powered-by' in headers}")

    assert headers.get("x-frame-options") == "DENY", "FAIL: X-Frame-Options missing or not DENY"
    assert headers.get("x-content-type-options") == "nosniff", "FAIL: X-Content-Type-Options missing"
    assert "default-src 'self'" in headers.get("content-security-policy", ""), "FAIL: Content-Security-Policy missing"
    assert "max-age=63072000" in headers.get("strict-transport-security", ""), "FAIL: HSTS missing"
    assert "server" not in headers, "FAIL: Server banner was not stripped!"
    assert "x-powered-by" not in headers, "FAIL: X-Powered-By banner was not stripped!"
    print("  [PASS] All security headers verified and technology banners suppressed.")

    print("\n" + "=" * 80)
    print("ALL 8 SECURITY & AUTHENTICATION INTEGRATION TESTS PASSED (100% SUCCESS)")
    print("=" * 80)


if __name__ == "__main__":
    run_security_verification()

