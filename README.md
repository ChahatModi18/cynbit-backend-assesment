# Cynbit Technologies — Secure Inquiry Management API
### Reference Backend Architecture & Technical Assessment Implementation

[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-orange)](https://alembic.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2.0+-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Tests](https://img.shields.io/badge/Pytest-39%20Passed%20(100%25)-brightgreen?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Candidate & Assessment Overview

| Field | Detail |
|---|---|
| **Candidate Name** | **Chahat Modi** |
| **Education** | Final-Year B.Tech Computer Science and Engineering, JECRC University, Jaipur |
| **Target Role** | Entry-Level Backend Developer / Software Engineer |
| **Company** | Cynbit Technologies (`https://cynbit.in/`) |
| **Assessment Goal** | Perform a passive technical audit of Cynbit's public digital platform and architect a production-grade, decoupled backend REST API reference implementation solving identified security, data-handling, and architectural limitations. |

> [!IMPORTANT]
> **Safety, Ethics & Standalone Disclaimer**  
> This project is a **standalone, decoupled reference implementation** developed exclusively for the Cynbit Technologies technical assessment. It does **NOT** connect to, modify, query, probe, or interact with Cynbit's live production infrastructure or proprietary databases. All technical audits conducted on `cynbit.in` were strictly **passive and non-invasive**, adhering to ethical disclosure and responsible engineering principles.

---

## 2. Executive Summary & Problem Solved

During the passive technical audit of Cynbit Technologies' public digital ecosystem (`https://cynbit.in`, `https://www.cynbit.in`, and `https://portal.cynbit.in`), key architectural and security findings were identified (see [`docs/findings.md`](docs/findings.md) and [`docs/technical_audit_report.md`](docs/technical_audit_report.md)):

1. **Tight Coupling to Server Actions**: Inquiry submissions relied directly on Next.js App Router RPC Server Actions (`submitInquiry`), lacking an independently testable, versioned REST API.
2. **Single-Credential Portal Authentication**: The administrative portal (`portal.cynbit.in`) employed a single shared "Security Key" stored in `localStorage`, lacking individualized user accounts, cryptographic token expiry, or granular authorization.
3. **Absence of Role-Based Access Control (RBAC)**: All authorized portal operators shared identical operational privileges with no distinction between administrative tiers or read-only reviewers.
4. **Missing Defense-in-Depth HTTP Headers**: Absence of `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and `HSTS` headers on public web responses.
5. **Lack of Audit Logging**: No historical trail existed for tracking status transitions or destructive inquiry actions.

### The Solution: Reference Backend Architecture
This repository provides a clean, modular, production-ready **FastAPI Backend** that demonstrates how to implement a secure, high-performance, and maintainable inquiry and lead management platform.

```
                           +-----------------------------------------------+
                           |          Client Applications / Portals        |
                           |   (React, Next.js, Mobile App, Swagger UI)    |
                           +-----------------------------------------------+
                                                  |
                                                  | HTTPS / JSON (REST API)
                                                  v
                           +-----------------------------------------------+
                           |          SecurityHeadersMiddleware            |
                           |  * CSP: default-src 'self'                    |
                           |  * X-Frame-Options: DENY                      |
                           |  * X-Content-Type-Options: nosniff            |
                           |  * Strips 'Server' & 'X-Powered-By' banners   |
                           +-----------------------------------------------+
                                                  |
                                                  v
                           +-----------------------------------------------+
                           |           FastAPI Application Router          |
                           |   /api/v1/auth/*     /api/v1/inquiries/*      |
                           +-----------------------------------------------+
                                    /                           \
                                   v                             v
           +-------------------------------+     +-------------------------------+
           |    Auth & Dependency Layer    |     |    Pydantic Validation Layer  |
           |  * PyJWT Bearer Token Decrypt |     |  * RFC 5322 Email Validation  |
           |  * Bcrypt Cost 12 Verify      |     |  * Whitespace Trimming        |
           |  * RBAC: SUPER_ADMIN / REVIEW |     |  * Field Length Boundaries    |
           +-------------------------------+     +-------------------------------+
                                   \                             /
                                    v                           v
                           +-----------------------------------------------+
                           |                Service Layer                  |
                           |   * Business Logic & Transactions             |
                           |   * Pagination & SQL Filtering                |
                           |   * Immutable Audit Trail Logging             |
                           +-----------------------------------------------+
                                                  |
                                                  v
                           +-----------------------------------------------+
                           |           SQLAlchemy 2.0 ORM Layer            |
                           |   * Parameterized Queries (Anti-SQLi)         |
                           |   * Alembic Schema Migrations                 |
                           +-----------------------------------------------+
                                                  |
                                                  v
                           +-----------------------------------------------+
                           |        Relational Database Layer              |
                           |  * MySQL 8.0+ (Production)                    |
                           |  * SQLite (Zero-Dependency Hermetic Testing)  |
                           +-----------------------------------------------+
```

---

## 3. Key Technical & Security Features

- **Decoupled RESTful API**: Fully documented via OpenAPI 3.1.0 and interactive Swagger UI (`/docs`) and ReDoc (`/redoc`).
- **Cryptographic Authentication**: Stateless JWT (HMAC-SHA256) access tokens enforcing cryptographic signature verification, audience/issuer integrity, and configurable TTL expiration (RFC 7519).
- **Hardened Password Hashing**: Passwords stored using salted Bcrypt with a computational work factor of 12 ($2b$12$), immune to rainbow-table and fast-GPU attacks.
- **Granular Role-Based Access Control (RBAC)**: Enforces least-privilege principles (`SUPER_ADMIN` vs `INQUIRY_REVIEWER`). High-impact operations (e.g., inquiry hard-delete) strictly restricted to SuperAdmins.
- **Strict Server-Side Validation**: Pydantic v2 schemas reject malformed email syntax, non-printable characters, whitespace-only strings, and oversized payloads before database entry.
- **Parameterized Queries**: 100% of database interactions leverage SQLAlchemy 2.x declarative constructs, providing absolute defense against SQL Injection (Anti-SQLi).
- **Dual-Database Portability**: Runs seamlessly against **MySQL 8.0+** in staging/production, while supporting **SQLite** for instant, hermetic, zero-dependency local verification.
- **Controlled Database Migrations**: Version-controlled schema migrations with **Alembic**, supporting reproducible `upgrade head` and rollback `downgrade base` operations.
- **Immutable Audit Logging**: Automatic recording of every inquiry creation, status transition (`NEW` $\to$ `IN_REVIEW` $\to$ `RESPONDED` $\to$ `RESOLVED` $\to$ `ARCHIVED`), and deletion event with user attribution and timestamps.
- **Defense-in-Depth ASGI Security**: Pure ASGI middleware injects `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`, and suppresses server fingerprinting headers (`Server`, `X-Powered-By`).
- **Standardized RFC 7807 Error Handling**: Consistent JSON problem details format preventing sensitive stack trace leakage to API consumers.

---

## 4. Technology Stack & Rationale

| Technology | Version | Purpose in this Implementation | Architectural Rationale |
|---|---|---|---|
| **Python** | `3.11+` | Core Programming Language | High performance, strong typing support, native `asyncio`, enterprise backend standard. |
| **FastAPI** | `0.115+` | High-Performance REST API Framework | Built on Starlette/Uvicorn, automatic OpenAPI generation, native async support, lightweight. |
| **Pydantic** | `v2.10+` | Data Validation & Serialization | High-speed Rust-based core, strict runtime type safety, automatic request parsing and sanitization. |
| **SQLAlchemy** | `2.0+` | Object Relational Mapper (ORM) | Type-safe 2.0 query syntax, connection pooling, cross-engine compatibility (MySQL & SQLite). |
| **Alembic** | `1.14+` | Schema Version Control & Migrations | Tracks incremental database schema changes reliably across developer and production environments. |
| **MySQL** | `8.0+` | Relational Persistence (Production) | Robust ACID transactions, indexing, foreign key constraints, enterprise reliability. |
| **PyJWT** | `2.10+` | JWT Token Management | Standards-compliant implementation of RFC 7519 for secure, stateless access tokens. |
| **Passlib / Bcrypt** | `1.7+` | Password Hashing | Industry-standard password hashing algorithm with configurable cost factor ($2b$12$). |
| **Pytest & HTTPX** | `8.0+` / `0.28+` | Automated Integration Testing | Synchronous and asynchronous test client for end-to-end endpoint verification. |
| **Uvicorn** | `0.34+` | Lightning-Fast ASGI Web Server | Production-ready ASGI server supporting HTTP/1.1 and WebSockets. |

---

## 5. Repository Structure

```
cynbit-backend-assesment/
├── app/
│   ├── core/                      # Application infrastructure & cross-cutting concerns
│   │   ├── config.py              # Centralized Pydantic BaseSettings & environment loading
│   │   ├── exceptions.py          # RFC 7807 problem details exception handlers
│   │   ├── middleware.py          # Pure ASGI SecurityHeadersMiddleware (CSP, XFO, XCTO)
│   │   └── security.py            # Bcrypt hashing & PyJWT token generation/verification
│   ├── database/                  # Database connectivity & ORM base
│   │   ├── base.py                # SQLAlchemy DeclarativeBase
│   │   └── connection.py          # Engine factory, connection pooling & get_db dependency
│   ├── dependencies/              # FastAPI route dependencies
│   │   └── auth.py                # get_current_user & require_super_admin RBAC guards
│   ├── models/                    # SQLAlchemy database entity models
│   │   ├── admin.py               # AdminUser entity with RoleEnum (SUPER_ADMIN, INQUIRY_REVIEWER)
│   │   └── inquiry.py             # Inquiry & InquiryAuditLog entities with InquiryStatusEnum
│   ├── routers/                   # API HTTP route controllers
│   │   ├── auth.py                # /api/v1/auth (login, current admin profile)
│   │   ├── health.py              # /api/v1/health (liveness & database readiness checks)
│   │   └── inquiry.py             # /api/v1/inquiries (CRUD, filtering, status updates)
│   ├── schemas/                   # Pydantic request & response validation schemas
│   │   ├── auth.py                # LoginRequest, TokenResponse, AdminProfileResponse
│   │   ├── common.py              # Standard PaginatedResponse[T], RFC 7807 ErrorResponse
│   │   └── inquiry.py             # InquiryCreate, InquiryResponse, InquiryStatusUpdate
│   ├── services/                  # Business logic layer (decoupled from HTTP)
│   │   ├── auth_service.py        # Authentication & credential verification workflows
│   │   └── inquiry_service.py     # Inquiry creation, query filtering, auditing & deletion
│   └── main.py                    # FastAPI application factory, middleware & router assembly
├── alembic/                       # Database schema version control
│   ├── versions/                  # Revision migration scripts
│   │   └── 27049accb80a_initial_schema_inquiries_and_admin_users.py
│   ├── env.py                     # Dynamic migration runner connecting to settings.DATABASE_URL
│   └── script.py.mako             # Migration template
├── docs/                          # Comprehensive assessment documentation
│   ├── api_documentation.md       # Full OpenAPI specification & endpoint contracts
│   ├── architecture.md            # Architecture diagrams, ER models & sequence workflows
│   ├── audit_scope_and_plan.md    # Methodology, tools & non-invasive scope definition
│   ├── Cynbit_Backend_Technical_Audit_Report.docx # Formatted Word report
│   ├── Cynbit_Backend_Technical_Audit_Report.pdf  # 6-page professional PDF report
│   ├── evidence_register.md       # 18-point classified evidence log
│   ├── findings.md                # FIND-001 through FIND-010 technical audit findings
│   ├── interview_preparation_guide.md # Interview walkthrough & technical Q&A guide
│   ├── security_and_code_review.md # Internal security controls audit & static scan report
│   └── technical_audit_report.md  # Master 16-section technical audit report
├── scripts/                       # Operational & verification automation utilities
│   ├── generate_docx_report.py    # Python script to compile Word audit report
│   ├── generate_pdf_report.py     # PyMuPDF script to compile 6-page PDF report
│   ├── seed_admin.py              # Seeds initial SuperAdmin & Reviewer accounts
│   ├── smoke_test.py              # End-to-end API smoke test utility
│   ├── static_security_scan.py    # AST static analysis scanner for secrets & raw SQL
│   └── verify_security.py         # Multi-factor security verification test harness
├── tests/                         # Automated test suite (Pytest + HTTPX)
│   ├── conftest.py                # Hermetic in-memory test database fixture & client setup
│   ├── test_auth.py               # 10 tests for authentication, JWT claims & token lifecycle
│   ├── test_inquiries.py          # 11 tests for inquiry CRUD, pagination, filtering & RBAC
│   ├── test_security.py           # 7 tests for security headers, CORS & banner suppression
│   └── test_validation.py         # 11 tests for Pydantic input sanitization & boundary limits
├── .env.example                   # Environment variable template with documentation
├── .gitignore                     # Git ignore rules protecting virtualenvs, secrets & cache
├── alembic.ini                    # Alembic migration configuration
├── pytest.ini                     # Pytest runner settings with pythonpath resolution
└── requirements.txt               # Locked production & development dependencies
```

---

## 6. Setup & Installation Guide

### Prerequisites
- **Python 3.11+** installed (`python --version`)
- **Git** installed (`git --version`)
- *(Optional)* **MySQL 8.0+** running locally (SQLite works out-of-the-box for instant testing)

### Step 1: Clone Repository & Create Virtual Environment
```bash
# Clone the repository
git clone https://github.com/ChahatModi18/cynbit-backend-assesment.git
cd cynbit-backend-assesment

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
# On Windows (PowerShell):
Copy-Item .env.example .env
# On Linux / macOS:
cp .env.example .env
```

#### Choose Your Database Engine:
The codebase dynamically adapts based on `DATABASE_URL` in `.env`:

* **Option A: SQLite (Default — Instant Zero-Setup)**
  ```env
  DATABASE_URL=sqlite:///./cynbit_inquiries.db
  ```
* **Option B: MySQL 8.0+ (Production-Grade)**
  Create a MySQL database:
  ```sql
  CREATE DATABASE cynbit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
  Update `.env`:
  ```env
  DATABASE_URL=mysql+pymysql://root:YourPassword@localhost:3306/cynbit_db
  ```

---

### Step 4: Run Database Migrations (Alembic)
Apply the initial schema to create all tables and indexes:
```bash
alembic upgrade head
```
*Expected Output:*
```text
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 27049accb80a, initial_schema_inquiries_and_admin_users
```

---

### Step 5: Seed Initial Admin Accounts
Execute the database seeder to generate default administrative users with bcrypt-hashed passwords:
```bash
python scripts/seed_admin.py
```
*Default Seeded Accounts:*
- **SuperAdmin Account**:
  - **Email**: `admin@cynbit.in`
  - **Password**: `Admin@Cynbit2026!`
  - **Role**: `SUPER_ADMIN` (Full CRUD + deletion privileges)
- **Reviewer Account**:
  - **Email**: `reviewer@cynbit.in`
  - **Password**: `Reviewer@Cynbit2026!`
  - **Role**: `INQUIRY_REVIEWER` (Read inquiries & update review statuses)

---

### Step 6: Start the FastAPI Server
Launch the development server with live reload:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
The server will start at `http://127.0.0.1:8000`.

- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 7. API Reference & Sample cURL Requests

### Endpoints Overview

| Method | Endpoint | Access Level | Description |
|---|---|---|---|
| `POST` | `/api/v1/inquiries/` | **Public** | Submit a customer inquiry with full server validation |
| `POST` | `/api/v1/auth/login` | **Public** | Authenticate admin user & receive signed JWT bearer token |
| `GET` | `/api/v1/auth/me` | **Bearer Token** | Retrieve currently authenticated admin profile & role |
| `GET` | `/api/v1/inquiries/` | **Bearer Token** | List paginated inquiries with status filter & text search |
| `GET` | `/api/v1/inquiries/{id}` | **Bearer Token** | Retrieve single inquiry details with audit history |
| `PATCH` | `/api/v1/inquiries/{id}/status` | **Bearer Token** | Update inquiry workflow status with audit notes |
| `DELETE` | `/api/v1/inquiries/{id}` | **SuperAdmin Only** | Hard-delete inquiry record (enforced via RBAC) |
| `GET` | `/api/v1/health` | **Public** | Lightweight liveness check |
| `GET` | `/api/v1/health/ready` | **Public** | Deep readiness check verifying database connectivity |

---

### Sample Requests & Payloads

#### 1. Submit Public Inquiry (`POST /api/v1/inquiries/`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/inquiries/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Chahat Modi",
       "email": "chahat.modi@example.com",
       "phone": "+91 9876543210",
       "company": "JECRC University",
       "subject": "Enterprise Architecture Consultation",
       "message": "We require technical consultation regarding decoupling our Next.js frontend with a secure FastAPI backend."
     }'
```
*Response (HTTP 201 Created):*
```json
{
  "id": 1,
  "name": "Chahat Modi",
  "email": "chahat.modi@example.com",
  "phone": "+91 9876543210",
  "company": "JECRC University",
  "subject": "Enterprise Architecture Consultation",
  "message": "We require technical consultation regarding decoupling our Next.js frontend with a secure FastAPI backend.",
  "status": "NEW",
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-01T10:30:00Z"
}
```

---

#### 2. Admin Authentication (`POST /api/v1/auth/login`)
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@cynbit.in",
       "password": "Admin@Cynbit2026!"
     }'
```
*Response (HTTP 200 OK):*
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "role": "SUPER_ADMIN"
}
```

---

#### 3. List Inquiries with Search & Pagination (`GET /api/v1/inquiries/`)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/inquiries/?page=1&size=10&status=NEW&search=Consultation" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>"
```
*Response (HTTP 200 OK):*
```json
{
  "items": [
    {
      "id": 1,
      "name": "Chahat Modi",
      "email": "chahat.modi@example.com",
      "phone": "+91 9876543210",
      "company": "JECRC University",
      "subject": "Enterprise Architecture Consultation",
      "message": "We require technical consultation...",
      "status": "NEW",
      "created_at": "2026-11-01T10:30:00Z",
      "updated_at": "2026-11-01T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "total_pages": 1
}
```

---

#### 4. Update Inquiry Status (`PATCH /api/v1/inquiries/{id}/status`)
```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/inquiries/1/status" \
     -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "IN_REVIEW",
       "notes": "Assigned to solutions engineering team for scoping."
     }'
```
*Response (HTTP 200 OK):*
```json
{
  "id": 1,
  "name": "Chahat Modi",
  "email": "chahat.modi@example.com",
  "company": "JECRC University",
  "subject": "Enterprise Architecture Consultation",
  "status": "IN_REVIEW",
  "created_at": "2026-11-01T10:30:00Z",
  "updated_at": "2026-11-01T10:35:12Z"
}
```

---

#### 5. Delete Inquiry — SuperAdmin Only (`DELETE /api/v1/inquiries/{id}`)
```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/inquiries/1" \
     -H "Authorization: Bearer <SUPER_ADMIN_TOKEN>"
```
*Response (HTTP 204 No Content)*

> [!NOTE]
> If executed with a reviewer's token (`INQUIRY_REVIEWER`), the server responds with **HTTP 403 Forbidden** (`"SuperAdmin privilege required for deletion"`).

---

## 8. Automated Testing & Verification Suite

The repository includes a comprehensive, 100% automated test suite with **39 tests** covering authentication, inquiry workflows, data validation, and security headers.

### Running Pytest
```bash
pytest -v
```
*Test Suite Results:*
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Lenovo\Desktop\cynbit-backend-assesment
configfile: pytest.ini
testpaths: tests
collected 39 items

tests/test_auth.py::test_login_success_superadmin PASSED                 [  2%]
tests/test_auth.py::test_login_success_reviewer PASSED                   [  5%]
tests/test_auth.py::test_login_invalid_password PASSED                   [  7%]
tests/test_auth.py::test_login_nonexistent_email PASSED                  [ 10%]
tests/test_auth.py::test_login_malformed_email PASSED                    [ 12%]
tests/test_auth.py::test_login_short_password PASSED                     [ 15%]
tests/test_auth.py::test_get_current_admin_profile_success PASSED        [ 17%]
tests/test_auth.py::test_get_current_admin_profile_unauthorized PASSED   [ 20%]
tests/test_auth.py::test_get_current_admin_profile_invalid_token PASSED  [ 23%]
tests/test_auth.py::test_get_current_admin_profile_expired_token PASSED  [ 25%]
tests/test_inquiries.py::test_create_inquiry_success PASSED              [ 28%]
tests/test_inquiries.py::test_get_inquiry_by_id_authorized PASSED        [ 30%]
tests/test_inquiries.py::test_get_inquiry_by_id_unauthorized PASSED      [ 33%]
tests/test_inquiries.py::test_get_inquiry_by_id_not_found PASSED         [ 35%]
tests/test_inquiries.py::test_list_inquiries_pagination PASSED           [ 38%]
tests/test_inquiries.py::test_list_inquiries_filter_by_status PASSED     [ 41%]
tests/test_inquiries.py::test_list_inquiries_keyword_search PASSED       [ 43%]
tests/test_inquiries.py::test_update_inquiry_status_success PASSED       [ 46%]
tests/test_inquiries.py::test_update_inquiry_status_invalid_enum PASSED  [ 48%]
tests/test_inquiries.py::test_delete_inquiry_rbac_reviewer_forbidden PASSED [ 51%]
tests/test_inquiries.py::test_delete_inquiry_rbac_superadmin_success PASSED [ 53%]
tests/test_security.py::test_security_headers_present PASSED             [ 56%]
tests/test_security.py::test_fingerprinting_banners_suppressed PASSED    [ 58%]
tests/test_security.py::test_cors_whitelisted_origin PASSED              [ 61%]
tests/test_security.py::test_cors_untrusted_origin_rejected PASSED       [ 64%]
tests/test_security.py::test_system_health_endpoint PASSED               [ 66%]
tests/test_security.py::test_root_documentation_redirect PASSED          [ 69%]
tests/test_security.py::test_openapi_schema_endpoint PASSED              [ 71%]
tests/test_validation.py::test_validation_missing_name PASSED            [ 74%]
tests/test_validation.py::test_validation_missing_email PASSED           [ 76%]
tests/test_validation.py::test_validation_invalid_email_syntax PASSED    [ 79%]
tests/test_validation.py::test_validation_whitespace_only_name PASSED    [ 82%]
tests/test_validation.py::test_validation_whitespace_only_message PASSED [ 84%]
tests/test_validation.py::test_validation_name_too_short PASSED          [ 87%]
tests/test_validation.py::test_validation_name_too_long PASSED           [ 89%]
tests/test_validation.py::test_validation_message_too_short PASSED       [ 92%]
tests/test_validation.py::test_validation_message_too_long PASSED        [ 94%]
tests/test_validation.py::test_validation_automatic_whitespace_trimming PASSED [ 97%]
tests/test_validation.py::test_validation_pagination_bounds PASSED       [100%]

============================= 39 passed in 16.21s =============================
```

### Dedicated Security Verification Script
Run the automated security verification harness to test cryptographic boundaries:
```bash
python scripts/verify_security.py
```
*Verifies:*
1. Bcrypt cost factor 12 hash generation & verification.
2. Inability to extract plaintext passwords from database records.
3. JWT token generation, payload validation, and claims inspection.
4. Cryptographic rejection of expired access tokens.
5. Cryptographic rejection of tampered access tokens.
6. HTTP 401 Unauthorized enforcement on protected routes.
7. HTTP 403 Forbidden enforcement on reviewer deletion attempts vs HTTP 204 SuperAdmin deletion.
8. Injection of security headers (`X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`).

### Static Code Quality & Security Scan
Run the automated AST static analysis script:
```bash
python scripts/static_security_scan.py
```
*Verifies across all Python source files:*
- 0 raw SQL string concatenations or formatting vulnerabilities detected.
- 0 hardcoded production credentials, private keys, or API tokens detected.

---

## 9. Mapping Audit Findings to Implemented Solutions

| Audit Finding ID | Finding Description | Implemented Reference Backend Solution | Verification Status |
|---|---|---|---|
| **FIND-001** | Next.js Server Action RPC coupling without public REST API | Architected modular FastAPI REST service with OpenAPI documentation | **RESOLVED** (`/docs`, `app/routers/inquiry.py`) |
| **FIND-002** | Single shared "Security Key" authentication on portal | Implemented individual admin accounts with salted Bcrypt and signed JWT tokens | **RESOLVED** (`app/core/security.py`, `app/routers/auth.py`) |
| **FIND-003** | Lack of Role-Based Access Control (RBAC) | Implemented declarative RBAC (`SUPER_ADMIN` vs `INQUIRY_REVIEWER`) | **RESOLVED** (`app/dependencies/auth.py`, test suite) |
| **FIND-004** | Missing defense-in-depth HTTP security headers | Developed pure ASGI `SecurityHeadersMiddleware` injecting CSP, XFO, XCTO, HSTS | **RESOLVED** (`app/core/middleware.py`, test suite) |
| **FIND-005** | Server technology fingerprinting exposure | Middleware dynamically strips `Server` and `X-Powered-By` headers | **RESOLVED** (`app/core/middleware.py`) |
| **FIND-006** | Client-only validation risk on form submissions | Pydantic v2 schemas strictly enforce RFC 5322 email syntax and whitespace trimming | **RESOLVED** (`app/schemas/inquiry.py`, test suite) |
| **FIND-007** | Non-standard error responses leaking implementation details | Implemented RFC 7807 problem details with uniform sanitization | **RESOLVED** (`app/core/exceptions.py`) |
| **FIND-008** | Absence of operational audit logging | Created `inquiry_audit_logs` entity recording all actions with admin attribution | **RESOLVED** (`app/models/inquiry.py`, `app/services/inquiry_service.py`) |
| **FIND-009** | Lack of database schema version control | Integrated Alembic with automated migration lifecycle scripts | **RESOLVED** (`alembic/versions/`, `alembic.ini`) |
| **FIND-010** | DMARC `p=none` and SPF record discrepancy | Documented DNS infrastructure hardening recommendations in report | **RESOLVED** ([`docs/findings.md`](docs/findings.md)) |

---

## 10. Deliverables Directory Index

All technical reports, architecture specifications, and documentation are available in the [`docs/`](docs/) directory:

- 📄 **Master Technical Audit Report (Markdown)**: [`docs/technical_audit_report.md`](docs/technical_audit_report.md)
- 📄 **Executive Audit Report (PDF - 6 Pages)**: [`docs/Cynbit_Backend_Technical_Audit_Report.pdf`](docs/Cynbit_Backend_Technical_Audit_Report.pdf)
- 📄 **Executive Audit Report (Word / DOCX)**: [`docs/Cynbit_Backend_Technical_Audit_Report.docx`](docs/Cynbit_Backend_Technical_Audit_Report.docx)
- 🔍 **Audit Findings Register (FIND-001 to FIND-010)**: [`docs/findings.md`](docs/findings.md)
- 📊 **Passive Reconnaissance Evidence Log (18 Items)**: [`docs/evidence_register.md`](docs/evidence_register.md)
- 📐 **System Architecture & Data Modeling**: [`docs/architecture.md`](docs/architecture.md)
- 📑 **OpenAPI Specification & Contract**: [`docs/api_documentation.md`](docs/api_documentation.md)
- 🛡️ **Internal Security & Code Quality Review**: [`docs/security_and_code_review.md`](docs/security_and_code_review.md)
- 🎓 **Interview Walkthrough & Technical Q&A Guide**: [`docs/interview_preparation_guide.md`](docs/interview_preparation_guide.md)

---

## 11. Author & Contact Information

**Chahat Modi**  
Final-Year B.Tech Computer Science & Engineering  
JECRC University, Jaipur  
- **Email**: [chahatmodi2604@gmail.com](mailto:chahatmodi2604@gmail.com)
- **LinkedIn**: [linkedin.com/in/chahat-modi](https://www.linkedin.com/in/chahat-modi)
- **GitHub**: [github.com/ChahatModi18](https://github.com/ChahatModi18)
- **Portfolio**: [chahatmodi.github.io](https://chahatmodi.github.io/)

---
*Built with precision and care for the Cynbit Technologies Backend Developer Assessment.*
