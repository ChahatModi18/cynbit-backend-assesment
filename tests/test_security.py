import pytest
from fastapi.testclient import TestClient


def test_security_headers_present(client: TestClient):
    """Verify that every HTTP response contains defense-in-depth security headers."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    headers = response.headers

    # FIND-005 Clickjacking defense
    assert headers.get("x-frame-options") == "DENY"

    # FIND-006 MIME Sniffing defense
    assert headers.get("x-content-type-options") == "nosniff"

    # FIND-004 Content Security Policy
    csp = headers.get("content-security-policy", "")
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp

    # HSTS
    hsts = headers.get("strict-transport-security", "")
    assert "max-age=63072000" in hsts

    # Referrer and Permissions
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("permissions-policy", "")


def test_fingerprinting_banners_suppressed(client: TestClient):
    """Verify that framework and server banners (FIND-007) are stripped."""
    response = client.get("/api/v1/health")
    headers = response.headers

    assert "server" not in headers, "FAIL: Server header was leaked!"
    assert "x-powered-by" not in headers, "FAIL: X-Powered-By header was leaked!"


def test_cors_whitelisted_origin(client: TestClient):
    """Verify that requests from whitelisted origins receive valid CORS response headers."""
    headers = {
        "Origin": "https://www.cynbit.in",
        "Access-Control-Request-Method": "POST"
    }
    response = client.options("/api/v1/inquiries", headers=headers)
    assert response.headers.get("access-control-allow-origin") == "https://www.cynbit.in"


def test_cors_untrusted_origin_rejected(client: TestClient):
    """Verify that untrusted origins do not receive permissive Access-Control-Allow-Origin headers."""
    headers = {
        "Origin": "https://untrusted-malicious-domain.com",
        "Access-Control-Request-Method": "POST"
    }
    response = client.options("/api/v1/inquiries", headers=headers)
    assert response.headers.get("access-control-allow-origin") != "https://untrusted-malicious-domain.com"


def test_system_health_endpoint(client: TestClient):
    """Verify system health verification endpoint and database connection probe."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data


def test_root_documentation_redirect(client: TestClient):
    """Verify that root requests redirect directly to interactive Swagger UI documentation."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [307, 308]
    assert response.headers.get("location") == "/docs"


def test_openapi_schema_endpoint(client: TestClient):
    """Verify that the OpenAPI JSON schema contract is publicly available and well-formed."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/api/v1/inquiries" in schema["paths"]
    assert "/api/v1/auth/login" in schema["paths"]

