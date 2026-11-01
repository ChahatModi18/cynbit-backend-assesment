# Cynbit Technologies — Backend Technical Assessment
## Candidate Interview Preparation & Technical Walkthrough Guide

---

**Candidate**: **Chahat Modi**  
**Role**: Entry-Level Backend Developer / Software Engineer  
**Institution**: Final-Year B.Tech Computer Science & Engineering, JECRC University, Jaipur  
**Company**: Cynbit Technologies (`https://cynbit.in/`)  
**Target Focus**: Technical Interview Preparation, System Architecture Defense & Codebase Walkthrough  

---

## 1. Candidate Narrative & Positioning

### How to Introduce Yourself
> *"I am Chahat Modi, a final-year Computer Science Engineering student at JECRC University, Jaipur. My primary focus is building robust, secure, and production-grade backend systems using Python, FastAPI, and MySQL, supported by SQLAlchemy and Alembic migrations.  
>  
> In addition to solving over 130 DSA and MySQL problems on LeetCode, I have engineered full-stack and backend systems such as **Bajaj Enterprises** (an enterprise bicycle showroom management platform featuring FastAPI, MySQL, JWT, Alembic, and bulk data processing) and **DigiMitra** (an AI-assisted digitalization assessment framework).  
>  
> For the Cynbit assessment, I treated the challenge as a real-world engineering assignment. I conducted a completely passive, ethical technical audit of Cynbit’s public digital ecosystem, identified architectural coupling and security opportunities, and built an end-to-end, production-ready reference backend with 39 automated tests, Alembic migrations, and defense-in-depth security headers."*

---

## 2. The 2-Minute Elevator Pitch

When asked: *"Can you give us a brief overview of what you did for this assessment?"*

> *"Certainly. The assessment had two core parts: an architectural audit and a reference backend implementation.  
>  
> First, I performed a strictly passive technical audit of `cynbit.in` and `portal.cynbit.in`. Without intrusive scanning or submitting live form data, I inspected DNS routing, TLS ciphers, HTTP response headers, and client bundle Server Actions. I identified 10 key findings, including tight frontend-to-backend coupling via Next.js Server Actions, a single shared 'Security Key' on the admin portal, missing defense-in-depth HTTP headers (like CSP and X-Frame-Options), and DMARC/SPF email configuration gaps.  
>  
> Second, to demonstrate how these challenges are solved cleanly in backend engineering, I developed a standalone, decoupled **Secure Inquiry Management REST API** in Python 3.11 using FastAPI and SQLAlchemy. It features:  
> 1. Individualized admin accounts with Bcrypt password hashing (work factor 12) and stateless PyJWT tokens with expiry.  
> 2. Declarative Role-Based Access Control distinguishing SuperAdmins from Inquiry Reviewers.  
> 3. Strict server-side validation using Pydantic v2 to sanitize inputs and prevent whitespace/malformed payloads.  
> 4. Version-controlled database migrations with Alembic and dual-engine support for MySQL and SQLite.  
> 5. Pure ASGI security middleware that enforces CSP, anti-clickjacking headers, and strips server banners.  
> 6. A 100% automated test suite with 39 passing Pytest tests covering security, validation, and inquiry lifecycles.  
>  
> The entire project is documented with Word and PDF reports, OpenAPI contracts, and clean Git commits."*

---

## 3. The 5-Minute Technical Walkthrough (Step-by-Step)

If the interviewer says: *"Walk me through your architecture and design decisions."*

Follow this 5-stage progression:

### Stage 1: The Problem Discovery (The Audit)
- **Passive Reconnaissance**: Used browser developer tools, `Resolve-DnsName`, and public asset inspection. Discovered that Cynbit's frontend is hosted on Vercel Edge (Mumbai BOM1 node), powered by Next.js App Router.
- **Server Actions Coupling**: Identified that the contact and careers forms invoke Next.js Server Actions directly (`submitInquiry`, `submitCandidateApplication`). While convenient for full-stack Next.js apps, this tightly couples data persistence to the React frontend, preventing external integration (e.g. CRM webhooks, mobile apps) and making standalone backend testing difficult.
- **Portal Security**: Found that `portal.cynbit.in` authenticated administrators via a single input labeled "Security Key" saved in `localStorage`. There were no individualized accounts, no password hashing, and no token expiry.

### Stage 2: Clean Layered Architecture
- Explain the decoupled structure:
  - **Routers** (`app/routers/`): Handle HTTP request routing, status codes, and endpoint documentation.
  - **Dependencies** (`app/dependencies/`): Handle authentication, token extraction, and RBAC authorization guards.
  - **Schemas** (`app/schemas/`): Pydantic v2 models for strict request validation, whitespace trimming, and response serialization.
  - **Services** (`app/services/`): Business logic layer completely separated from HTTP concerns.
  - **ORM & Models** (`app/models/`, `app/database/`): SQLAlchemy 2.0 declarative models and connection management.
- *Why this matters*: Separation of concerns ensures testability. The business logic can be tested without spinning up an HTTP server.

### Stage 3: Security & Cryptography Implementation
- **Password Hashing**: Bcrypt with automated salt generation and computational work factor 12 ($2b$12$). Stored hashes are resistant to GPU dictionary attacks.
- **Stateless Tokens**: RFC 7519 JWT access tokens signed with HMAC-SHA256 (`HS256`), containing `sub` (user ID), `role`, `email`, and `exp` (30 minutes TTL).
- **Role-Based Access Control**: Standard reviewers can read inquiries and update statuses (`NEW` $\to$ `IN_REVIEW` $\to$ `RESPONDED` $\to$ `RESOLVED`). Destructive deletion (`DELETE /api/v1/inquiries/{id}`) is strictly guarded by `require_super_admin`, returning `403 Forbidden` to non-superadmins.
- **Pure ASGI Middleware**: Built `SecurityHeadersMiddleware` directly on the ASGI `receive`/`send` protocol. Injects `Content-Security-Policy: default-src 'self'`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and strips `Server` and `X-Powered-By` banners to prevent technology fingerprinting.

### Stage 4: Database & Migration Lifecycle
- **Schema Design**: Normalized schema with `admin_users`, `inquiries`, and `inquiry_audit_logs`. `inquiry_audit_logs` maintains a permanent audit trail linked via a foreign key (`inquiry_id`) with `CASCADE` deletion.
- **Indexing Strategy**: B-Tree indexes created on `email`, `status`, and `created_at` in the `inquiries` table to optimize frequent dashboard filters and sorting queries.
- **Alembic Version Control**: Configured `alembic/env.py` to dynamically bind to `settings.DATABASE_URL` with `render_as_batch=True`, ensuring migrations work seamlessly across both production MySQL 8.0+ and SQLite.

### Stage 5: Testing & Verification Rigor
- **Pytest + HTTPX**: 39 automated tests executed with 100% pass rate in 16.2 seconds.
- **Hermetic Testing**: Used `conftest.py` with an in-memory SQLite database (`sqlite:///:memory:`) and FastAPI `app.dependency_overrides` so tests run rapidly in complete isolation without polluting production data.
- **Negative & Boundary Testing**: 11 dedicated validation tests ensuring malformed emails, empty strings, whitespace-only fields, and character boundary overruns are rejected with RFC 7807 problem details.

---

## 4. Deep-Dive Technical Questions & High-Scoring Answers

### Category A: Python & FastAPI Architecture

#### Q1: Why did you choose FastAPI over Flask or Django?
> **Answer**:
> *"FastAPI was selected for three clear engineering reasons:  
> 1. **Performance & Asynchronous I/O**: FastAPI is built on Starlette and Uvicorn, offering asynchronous I/O performance on par with Go and Node.js. For I/O-bound operations like database queries and third-party notifications, async execution prevents thread starvation.  
> 2. **Automatic Type Validation & OpenAPI**: By integrating Pydantic v2, request parsing, type coercion, and validation happen automatically before execution reaches the router. Furthermore, interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) are generated with zero manual documentation effort.  
> 3. **Clean Dependency Injection**: FastAPI's `Depends()` system allows clean, composable injection of database sessions, authentication context, and RBAC authorization checks, making unit and integration testing straightforward via `dependency_overrides`."*

#### Q2: When should an endpoint function be defined as `async def` vs `def` in FastAPI?
> **Answer**:
> *"In FastAPI, if an endpoint performs blocking, synchronous I/O (such as standard SQLAlchemy blocking database calls or heavy CPU computation), defining it as `def` instructs FastAPI to automatically run it on a separate background threadpool (via AnyIO), preventing the main event loop from blocking.  
> Conversely, if the endpoint calls non-blocking asynchronous libraries (such as `httpx.AsyncClient` or `AsyncSession` with asyncpg/aiomysql), `async def` should be used so the coroutine yields control back to the event loop during awaitable I/O. In our reference implementation, endpoints calling synchronous SQLAlchemy sessions are defined as `def` to avoid blocking the ASGI event loop."*

#### Q3: Why did you write a custom pure ASGI middleware instead of using Starlette's `BaseHTTPMiddleware`?
> **Answer**:
> *"Starlette's `BaseHTTPMiddleware` wraps request and response streams inside an internal context manager. This has well-documented drawbacks in production: it introduces measurable overhead, can cause issues with streaming responses, and can mask or mismanage ASGI connection cancelation.  
> By implementing `SecurityHeadersMiddleware` as a pure ASGI interface taking `(scope, receive, send)`, we inspect and inject headers directly into the `http.response.start` message tuple with minimal overhead and zero event-loop deadlocks."*

---

### Category B: Databases, SQL & Alembic Migrations

#### Q1: Why use MySQL rather than a NoSQL document database (like MongoDB) for this inquiry system?
> **Answer**:
> *"Inquiry and administrative data is inherently structured and relational:  
> 1. **Data Integrity & Constraints**: Inquiries require strict schema validation, unique constraints, and foreign key relationships (such as linking audit logs to inquiries via `inquiry_id` with cascading constraints).  
> 2. **ACID Transactions**: Financial or enterprise client inquiries require transactional guarantees—if an inquiry status update succeeds, the corresponding audit log entry must commit atomically.  
> 3. **Predictable Query Patterns**: The primary administrative queries involve structured filtering by status, email indexing, and date-range sorting, which B-tree indexes in relational engines like MySQL handle efficiently with minimal resource overhead."*

#### Q2: How does SQLAlchemy protect against SQL Injection?
> **Answer**:
> *"SQLAlchemy prevents SQL injection by abstracting SQL execution through parameterized queries. Instead of formatting user input into a raw SQL string (e.g. `WHERE email = '` + email + `'`), SQLAlchemy compiles ORM statements (`select(Inquiry).where(Inquiry.email == email)`) into parameterized SQL (`WHERE inquiries.email = :email_1`).  
> The database driver transmits the query structure and parameter values separately. The database engine never interprets the parameter value as executable SQL syntax, completely neutralizing SQL Injection attacks. In our codebase, 100% of queries use parameterized SQLAlchemy expressions, verified by our static AST scanner."*

#### Q3: What is the purpose of Alembic, and why did you configure `render_as_batch=True`?
> **Answer**:
> *"Alembic provides programmatic version control for relational database schemas. Without migrations, database changes (adding columns, modifying constraints) require manual SQL scripts that are error-prone and lead to schema drift across development, staging, and production.  
> In our `alembic/env.py`, we enabled `render_as_batch=True`. This is crucial for SQLite compatibility during local development and testing. SQLite has architectural limitations regarding `ALTER TABLE` operations (it cannot drop columns or modify constraints directly). Alembic's batch mode creates a new temporary table with the updated schema, copies existing records, drops the old table, and renames the new table, ensuring migrations run reliably on both MySQL and SQLite."*

#### Q4: Explain your indexing strategy on the `inquiries` table.
> **Answer**:
> *"We placed B-Tree indexes on three critical columns:  
> 1. `email` (`ix_inquiries_email`): Enables $O(\log N)$ lookup when searching for prior inquiries submitted by the same client.  
> 2. `status` (`ix_inquiries_status`): Enables high-performance filtering on the admin dashboard (e.g., retrieving only `NEW` or `IN_REVIEW` inquiries).  
> 3. `created_at` (`ix_inquiries_created_at`): Inquiries are almost always sorted chronologically (newest first). Indexing `created_at` avoids expensive full-table filesorts in MySQL (`ORDER BY created_at DESC`)."*

---

### Category C: Security, Cryptography & HTTP Headers

#### Q1: What was wrong with the security on `portal.cynbit.in`, and how did your solution fix it?
> **Answer**:
> *"Our passive audit revealed that `portal.cynbit.in` had a single input field titled 'Security Key' that saved a static key in the browser's `localStorage`.  
> This presented several security risks:  
> 1. **No Accountability**: All administrators shared the same password. If an inquiry was deleted, it was impossible to determine which team member performed the action.  
> 2. **No Expiration**: The key remained in `localStorage` indefinitely, vulnerable to XSS token theft.  
> 3. **No Revocation or Rotation**: Revoking access for a departed team member required changing the shared key for everyone.  
>  
> We resolved this by implementing:  
> - Individual administrator accounts (`admin_users` table).  
> - Bcrypt password hashing ($2b$12$) with unique per-user salts.  
> - Cryptographically signed JWT tokens with 30-minute expiry (`exp`), verified by HMAC-SHA256.  
> - Granular RBAC (`SUPER_ADMIN` vs `INQUIRY_REVIEWER`) with immutable audit logging."*

#### Q2: Why is Bcrypt preferred over MD5 or SHA-256 for password storage?
> **Answer**:
> *"MD5 and SHA-256 are general-purpose cryptographic hash functions designed to be extremely fast. Because of their speed, an attacker with a modern consumer GPU can compute billions of SHA-256 hashes per second, making offline dictionary and brute-force cracking trivial.  
> Bcrypt is a key-derivation function based on the Blowfish cipher that is deliberately slow and computationally intensive. It includes a configurable work factor (we configured cost 12, requiring $2^{12} = 4096$ iterations) and incorporates a random 128-bit salt directly into the output hash. This defeats precomputed rainbow table attacks and makes GPU brute-forcing economically and computationally infeasible."*

#### Q3: What is Clickjacking, and how does your middleware prevent it?
> **Answer**:
> *"Clickjacking (UI redressing) is an attack where a malicious site embeds our web application inside an invisible `<iframe>` and lures an authenticated user into clicking buttons on the transparent layer (e.g., triggering an inquiry deletion).  
> We mitigate this at the HTTP protocol layer by injecting two headers in `SecurityHeadersMiddleware`:  
> 1. `X-Frame-Options: DENY`: Tells legacy and modern browsers never to allow the page to be rendered within a frame.  
> 2. `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`: Modern W3C standard header that explicitly forbids any domain (including self) from embedding the application in frames or iframes."*

#### Q4: Why is MIME type sniffing dangerous, and what does `X-Content-Type-Options: nosniff` do?
> **Answer**:
> *"MIME type sniffing is a browser behavior where the browser attempts to guess the content type of a file by inspecting its byte content rather than trusting the `Content-Type` header sent by the server. If an attacker uploads a malicious HTML/JavaScript file disguised as an image or text file, a sniffing browser might execute it as script in the user's browser context (XSS).  
> Setting `X-Content-Type-Options: nosniff` strictly forces the browser to honor the declared MIME type, preventing execution of disguised payloads."*

---

### Category D: Testing, Quality & Engineering Trade-offs

#### Q1: How did you test the backend, and why did you use an in-memory SQLite database?
> **Answer**:
> *"We built an automated test suite with 39 test cases using Pytest and HTTPX `TestClient`.  
> In `tests/conftest.py`, we created an isolated in-memory SQLite database (`sqlite:///:memory:`) using `StaticPool`. In the Pytest fixture, `Base.metadata.create_all()` builds the entire schema before each test, and `dependency_overrides[get_db]` injects the in-memory session into FastAPI.  
> This ensures:  
> 1. **Complete Hermetic Isolation**: Tests run independently without side effects or race conditions.  
> 2. **High Speed**: The entire 39-test suite executes in ~16 seconds in memory.  
> 3. **Zero External Dependencies**: Anyone cloning the repository can run `pytest -v` immediately without needing a running MySQL instance."*

#### Q2: Why didn't you implement Redis, Celery, or Kafka in this assessment?
> **Answer**:
> *"In software engineering, introducing tools without a corresponding requirement is premature over-engineering.  
> For an inquiry submission and review service handling moderate business traffic:  
> 1. Adding Redis introduces an external caching dependency and distributed cache-invalidation complexity when standard MySQL queries with proper indexes execute in sub-millisecond times.  
> 2. Adding Celery and RabbitMQ/Kafka requires background worker processes, monitoring daemons, and broker maintenance.  
>  
> However, our architecture is designed for clean future evolution: if asynchronous email notifications or webhook deliveries are required, we can introduce Celery tasks or FastAPI `BackgroundTasks` without altering the core database models or API contracts."*

---

## 5. Candidate Checklist Before the Interview

- [x] Read and understand all 10 audit findings in [`docs/findings.md`](../docs/findings.md).
- [x] Review the 16-section master report in [`docs/technical_audit_report.md`](../docs/technical_audit_report.md).
- [x] Execute `pytest -v` locally and verify that all 39 tests pass.
- [x] Run `python scripts/verify_security.py` and review the terminal verification outputs.
- [x] Inspect `app/main.py`, `app/core/middleware.py`, and `app/dependencies/auth.py` so you can comfortably explain each line of code.
- [x] Be prepared to launch the server (`uvicorn app.main:app --reload`) and demonstrate interactive endpoints on Swagger UI (`http://127.0.0.1:8000/docs`).

---
*Prepared by Chahat Modi — Ready for Technical Discussion and Architectural Defense.*
