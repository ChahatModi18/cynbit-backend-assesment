# Cynbit Technologies — Backend Technical Audit Scope and Investigation Plan

## 1. Executive Context

- **Target Organization**: Cynbit Technologies (Jaipur, Rajasthan, India)
- **Target URL**: `https://cynbit.in/` (Redirects to canonical: `https://www.cynbit.in/`)
- **Subdomains Observed**: `https://portal.cynbit.in/`
- **Auditor**: Chahat Modi (Final-Year B.Tech CSE, JECRC University, Jaipur)
- **Role**: Backend Developer Technical Assessment Submission
- **Date**: November 1, 2026
- **Mode of Assessment**: Passive, non-intrusive, authorized observational analysis only.

---

## 2. Assessment Scope & Boundaries

### In-Scope Activities (Passive Only)
1. **Public HTTP Response Inspection**: Header inspection, caching directives, redirection behavior, status codes.
2. **TLS / Cryptographic Parameter Analysis**: Protocol version (TLS 1.2 / 1.3), cipher suites, certificate issuer and validity.
3. **DNS & Mail Security Records**: Resolution of A, CNAME, MX, TXT (SPF), NS, and DMARC records.
4. **Public Site Architecture & Endpoints**: Crawl analysis via `sitemap.xml` and `robots.txt`.
5. **Client-Side Asset & Bundle Inspection**: Analysis of publicly delivered Next.js JavaScript chunks, visible forms, state management, and Server Action references.
6. **Authentication & Session Analysis**: Inspection of the publicly exposed login mechanism on `portal.cynbit.in`.
7. **Performance & CDN Architecture**: Edge caching behavior, asset preloading, and server-side rendering indicators.

### Strict Out-of-Scope Activities (Ethical Boundaries)
- **NO Active Exploitation**: No SQL injection payloads, XSS payloads, or command injections.
- **NO Authentication Bypasses or Credential Stuffing**: No brute-forcing the portal's "Security Key" or fuzzing endpoints.
- **NO Form Submissions**: No test data or spam submitted via `/contact` or `/careers` forms.
- **NO Denial of Service / Stress Testing**: No load testing, high-volume automated fuzzing, or resource exhaustion.
- **NO Modifying or Deleting External Data**.

---

## 3. Investigation Methodology

The technical audit follows an evidence-based approach aligning with the OWASP Web Security Testing Guide (WSTG) passive guidelines:

```
[Phase 1: Passive Reconnaissance]
         │
         ├──► 1. Network & TLS Layer (DNS, IP, Certificates, Protocols)
         ├──► 2. Infrastructure & Hosting (CDN, Edge Nodes, Server Identity)
         ├──► 3. Web Framework & Routing (Next.js App Router, SSR/SSG, Server Actions)
         ├──► 4. Security Headers & CORS (HSTS, CSP, XFO, CORS Policies)
         ├──► 5. Authentication & Access Control (Single-key model, LocalStorage, Route guards)
         └──► 6. Data Handling & Forms (Input validation, Server Actions, Error handling)
```

### Classification Standards
All findings and statements are strictly categorized into one of four verified tiers:
- **[OBSERVED]**: Directly verified through network responses, HTTP headers, DNS lookups, or script bundles.
- **[INFERRED]**: A logical, technical deduction based on visible architectural patterns.
- **[POTENTIAL RISK]**: A plausible technical risk that cannot be definitively proven without internal source or infrastructure access.
- **[NOT VERIFIABLE]**: An architectural aspect that requires internal database, backend code, or deployment access to confirm.

---

## 4. Assessment Deliverables Roadmap

1. **Phase 1**: Website Investigation, Passive Reconnaissance & Evidence Register.
2. **Phase 2**: Comprehensive Backend Technical Audit Report & Findings Register.
3. **Phase 3**: Standalone Reference Backend Architecture Design (FastAPI + MySQL + SQLAlchemy + Alembic + JWT).
4. **Phase 4**: Incremental Backend Implementation (Inquiry API, Models, Schemas, Routers).
5. **Phase 5**: Database Integration (MySQL, Alembic migrations, Transactions).
6. **Phase 6**: Authentication & Security Hardening (JWT, Password Hashing, RBAC, Rate Limiting, Security Middleware).
7. **Phase 7**: Automated Testing & Quality Assurance (Pytest + HTTPX suite).
8. **Phase 8**: Security Audit & Static Analysis Review.
9. **Phase 9**: Final Documentation (README.md, Word `.docx`, PDF report).
10. **Phase 10**: Git Version Control & Public GitHub Publication.
11. **Phase 11**: Verification & Interview Preparation Walkthrough.

