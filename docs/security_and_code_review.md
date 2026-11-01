# Cynbit Technologies — Security & Code Quality Review

---

**Project**: Secure Inquiry Management API Reference Implementation  
**Auditor & Backend Engineer**: Chahat Modi (Final-Year B.Tech CSE, JECRC University, Jaipur)  
**Date**: November 1, 2026  
**Document Version**: 1.0 (Phase 8 Security Audit)  

---

## 1. Executive Summary

This document details the internal code quality, static analysis, and security controls review conducted across the Cynbit reference backend codebase. The review verifies that the security and architectural vulnerabilities identified during the website audit (FIND-001 through FIND-010) are comprehensively addressed without introducing secondary security liabilities.

---

## 2. Security Audit Matrix

| Security Dimension | Codebase Implementation | Verification Method | Status |
|---|---|---|---|
| **SQL Injection Defense** | All queries utilize SQLAlchemy 2.x parameterized expressions (`select()`, `where()`, `or_()`, `ilike()`). No string interpolation or raw SQL concatenation exists. | Static AST regex analysis & Pytest suite | **PASS (100% Parameterized)** |
| **Password Storage** | Bcrypt one-way hashing with automated per-user salt and cost factor of 12 (`hash_password`, `verify_password`). Passwords never stored or returned in plaintext. | Unit tests & DB record byte inspection | **PASS (Bcrypt $2b$12$)** |
| **Authentication & Tokens** | Signed JWT access tokens (HMAC-SHA256) enforcing `sub`, `role`, `email`, `exp`, `iat`, `iss`. Expired and tampered tokens are rejected with 401. | PyJWT signature tampering & expiration tests | **PASS (Stateless JWT)** |
| **Role-Based Access Control** | Declarative `require_super_admin` dependency restricts destructive endpoints (`DELETE /inquiries/{id}`). Non-superadmins receive 403 Forbidden. | Reviewer vs SuperAdmin automated tests | **PASS (RBAC Enforced)** |
| **Server-Side Validation** | Strict Pydantic v2 schemas (`InquiryCreate`, `LoginRequest`). Enforces string trimming, whitespace-only rejection, RFC 5322 email syntax, and length limits. | 11 negative & boundary test cases | **PASS (Pydantic v2)** |
| **Information Disclosure** | Centralized RFC 7807 problem details. Generic error messages on login (`"Invalid email or password"`) prevent user enumeration. 500 handler logs tracebacks internally but returns generic message. | Negative authentication & error tests | **PASS (Sanitized)** |
| **Clickjacking Defense** | Pure ASGI `SecurityHeadersMiddleware` injects `X-Frame-Options: DENY` and `frame-ancestors 'none'`. | Response header assertion tests | **PASS (XFO DENY)** |
| **MIME Sniffing Defense** | Middleware injects `X-Content-Type-Options: nosniff`. | Response header assertion tests | **PASS (XCTO nosniff)** |
| **Content Security Policy** | Middleware injects `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`. | Response header assertion tests | **PASS (CSP Injected)** |
| **Technology Fingerprinting** | Middleware dynamically strips `server` and `x-powered-by` headers on all outgoing responses. | Header inspection tests | **PASS (Banners Stripped)** |
| **Cross-Origin Security** | FastAPI `CORSMiddleware` restricted to explicitly whitelisted client origins (`settings.cors_origins_list`). Untrusted origins rejected. | CORS preflight OPTIONS tests | **PASS (Restricted CORS)** |
| **Credential & Secret Safety** | Zero hardcoded production secrets. `.env` file strictly ignored in `.gitignore`. `.env.example` provides placeholders only. | Static secret scanner & disk audit | **PASS (No Leaked Secrets)** |

---

## 3. Categorized Security Controls

### 3.1 Implemented Controls (Verified in Reference Backend)
1. **Stateless JWT Authentication (RFC 7519)**: Eliminates single shared "Security Key" risk by issuing cryptographic, expiring tokens to individual users.
2. **Bcrypt Password Hashing**: Salted hashing with work factor $\ge 12$ protects passwords at rest against offline rainbow-table cracking.
3. **Role-Based Access Control (RBAC)**: Enforces least-privilege principles by restricting inquiry deletion to `SUPER_ADMIN` accounts.
4. **Server-Side Input Sanitization**: Strips leading/trailing whitespace, rejects whitespace-only inputs, and enforces character bounds independent of client validation.
5. **Defense-in-Depth HTTP Headers**: Injects `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`, and `Strict-Transport-Security`.
6. **Framework Banner Suppression**: Strips `server` and `x-powered-by` response headers to minimize reconnaissance exposure.
7. **Restricted CORS Policy**: Only permits whitelisted domains (`https://cynbit.in`, `https://www.cynbit.in`, `http://localhost:3000`) to execute cross-origin requests.
8. **Structured Error Handling (RFC 7807)**: Emits uniform JSON error objects without exposing internal database errors, SQL queries, or stack traces.
9. **Dual-Environment Database Abstraction**: Supports production MySQL 8.0+ and hermetic in-memory SQLite for testing with zero external dependencies.
10. **Immutable Audit Logging**: Every inquiry creation, status update, and deletion is recorded in `inquiry_audit_logs` with admin attribution.

---

### 3.2 Controls Considered but Not Implemented (Scope & Simplicity Trade-Offs)
1. **Redis-Backed Token Revocation / Blacklisting**:
   - *Rationale*: For an entry-level assessment, maintaining stateless JWTs with short expirations (30 minutes) provides strong security without requiring a live Redis cluster or Celery worker infrastructure.
   - *Consideration*: In high-concurrency enterprise deployments, a Redis blacklist allows instantaneous revocation before token TTL expires.
2. **Multi-Factor Authentication (TOTP / WebAuthn)**:
   - *Rationale*: Adding TOTP QR code generation and two-step verification adds frontend dependency complexity. The architecture is prepared for MFA via `AdminUser` model extension.
3. **Automated CAPTCHA / Proof-of-Work on Public Inquiries**:
   - *Rationale*: External services (e.g. Cloudflare Turnstile, Google reCAPTCHA) require third-party API keys and external internet connectivity during local testing.
   - *Consideration*: Should be enforced at the API gateway or reverse proxy layer in production.

---

### 3.3 Limitations and Future Improvements
1. **Rate Limiting at Edge / Reverse Proxy**:
   - Introduce token-bucket rate limiting via Nginx or Cloudflare (e.g., maximum 5 inquiry submissions per IP per minute) to prevent Denial-of-Service spamming.
2. **Asynchronous Notification Queue**:
   - Dispatch real-time email notifications (via Celery or ARQ) to the solutions engineering team when a high-priority enterprise inquiry is submitted.
3. **Read Replica & Query Caching**:
   - For high-volume inquiry reading, configure read replicas in MySQL and cache frequent paginated queries in Redis.
