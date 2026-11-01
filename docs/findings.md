# Cynbit Technologies — Security and Technical Findings Register

**Assessment Scope**: Passive observational analysis of `https://cynbit.in/` and `https://portal.cynbit.in/`  
**Assessment Date**: November 1, 2026  
**Auditor**: Chahat Modi (Final-Year B.Tech CSE, JECRC University, Jaipur)  
**Role**: Backend Developer Technical Assessment  

---

## Summary of Findings

| Finding ID | Category | Severity | Confidence Level | Title |
|---|---|---|---|---|
| **FIND-001** | Authentication & Access Control | **High** | Confirmed (High) | Single-Factor Shared "Security Key" Administrative Authentication |
| **FIND-002** | Session Management | **Medium** | Confirmed (High) | Client-Side Session Activity Storage in LocalStorage |
| **FIND-003** | Web Security & CORS | **Medium** | Confirmed (High) | Permissive Wildcard Cross-Origin Resource Sharing on HTML Responses |
| **FIND-004** | Web Application Security | **Medium** | Confirmed (High) | Absence of Content Security Policy (CSP) Defense Header |
| **FIND-005** | Web Application Security | **Medium** | Confirmed (High) | Absence of Clickjacking Defense (`X-Frame-Options` / `frame-ancestors`) |
| **FIND-006** | Web Application Security | **Low** | Confirmed (High) | Missing `X-Content-Type-Options: nosniff` Header |
| **FIND-007** | Information Disclosure | **Low** | Confirmed (High) | Framework Fingerprinting via `X-Powered-By: Next.js` |
| **FIND-008** | Information Disclosure | **Informational** | Confirmed (High) | Administrative Route Enumeration via `robots.txt` |
| **FIND-009** | Email & Domain Security | **Low** | Confirmed (High) | Inconsistent SPF Records and Unenforced DMARC Policy (`p=none`) |
| **FIND-010** | Backend Architecture | **Informational** | Confirmed (High) | Coupled Server Action Architecture Lacking Decoupled REST API Contract |

---

## Detailed Findings

---

### FIND-001: Single-Factor Shared "Security Key" Administrative Authentication

- **Finding ID**: FIND-001
- **Category**: Authentication & Access Control
- **Severity**: **High**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
The administrative portal at `https://portal.cynbit.in/` presents a login screen requesting only a "Security Key" (a single password field). There is no provision for entering a username, corporate email address, or individual account identifier. Client bundle analysis reveals that the form directly bundles the entered password into a `FormData` object and invokes the Next.js Server Action `loginToPortal` (`40d93da1cc26de4ef37bcb273184b7141ef77a50f8`).

#### Evidence
De-obfuscated script extract from `portal.cynbit.in/_next/static/chunks/app/portal/page-ba479285e84c64b5.js`:
```javascript
let l = (0, s.createServerReference)(
  "40d93da1cc26de4ef37bcb273184b7141ef77a50f8",
  s.callServer,
  void 0,
  s.findSourceMapURL,
  "loginToPortal"
);

function i() {
  let [e, r] = (0, n.useState)(""), [t, s] = (0, n.useState)(""), [i, o] = (0, n.useState)(!1);
  async function c(r) {
    r.preventDefault(), o(!0), s("");
    let t = new FormData();
    t.append("password", e);
    let a = await l(t);
    if (a.success) {
      try {
        localStorage.setItem("cynbit_portal_last_activity", Date.now().toString());
      } catch (e) {}
      window.location.href = "/dashboard";
    } else {
      s(a.error || "Login failed"), o(!1);
    }
  }
  // Form renders single password input:
  // <input type="password" value={e} onChange={...} placeholder="••••••••" required />
}
```

#### Impact
1. **Lack of Non-Repudiation**: Because all administrators share the same security key, any mutation (such as reviewing, updating, or deleting customer inquiries or job applicant records) cannot be attributed to a specific person.
2. **Revocation Overhead**: If an employee, contractor, or intern with knowledge of the security key departs, the key must be rotated across the entire team simultaneously.
3. **No Multi-Factor Authentication (MFA)**: A single secret compromise (via shoulder-surfing, credential stuffing, or accidental exposure) gives an attacker full administrative access.
4. **No Account Lockout or Per-User Rate Limiting**: In a shared credential architecture, applying brute-force lockout rules would lock out all legitimate administrators if an attacker attacks the single portal key.

#### Recommended Solution
1. Replace single-key authentication with **Individual Identity Management**:
   - Each administrator authenticates with an individual email and strong password.
   - Passwords must be hashed using modern cryptographic algorithms (`Argon2id` or `bcrypt` with work factor $\ge 12$).
2. Implement **JSON Web Token (JWT) or Secure Server Sessions**:
   - Issue short-lived access tokens (e.g., 15–30 minutes) and secure refresh tokens.
   - Enforce cryptographic signature verification on all protected endpoints (`/api/v1/inquiries`, etc.).
3. Introduce **Role-Based Access Control (RBAC)**:
   - Differentiate privileges (e.g., `SuperAdmin`, `InquiryReviewer`, `HRAdmin`).
4. Enforce **Multi-Factor Authentication (MFA)**:
   - Require Time-based One-Time Passwords (TOTP via Google Authenticator/Authy) for administrative accounts.

---

### FIND-002: Client-Side Session Activity Storage in LocalStorage

- **Finding ID**: FIND-002
- **Category**: Session Management
- **Severity**: **Medium**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
Upon successful administrative authentication on `portal.cynbit.in`, the application writes a session timestamp directly into the browser's `localStorage`:
```javascript
localStorage.setItem("cynbit_portal_last_activity", Date.now().toString());
```

#### Evidence
Verified in client chunk `page-ba479285e84c64b5.js`:
```javascript
if (a.success) {
  try {
    localStorage.setItem("cynbit_portal_last_activity", Date.now().toString());
  } catch (e) {}
  window.location.href = "/dashboard";
}
```

#### Impact
1. **Client-Side Script Accessibility**: HTML5 `localStorage` is completely accessible to any JavaScript running within the page origin (`window.localStorage`). Unlike cookies configured with the `HttpOnly` flag, data stored in `localStorage` cannot be shielded from Cross-Site Scripting (XSS) vectors.
2. **Session Invalidation Vulnerabilities**: If session validity or timeout checks rely on client-manipulated timestamps in `localStorage`, a local user or script can overwrite `cynbit_portal_last_activity` to keep an expired session active on the client.

#### Recommended Solution
1. Manage all session expirations and timeouts strictly on the server:
   - Calculate idle timeout and maximum lifetime on the backend using the token's `exp` and `iat` claims or server session store.
2. Deliver authentication credentials using `HttpOnly`, `Secure`, `SameSite=Strict` cookies.

---

### FIND-003: Permissive Wildcard Cross-Origin Resource Sharing on HTML Responses

- **Finding ID**: FIND-003
- **Category**: Web Security & CORS
- **Severity**: **Medium**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
Both the apex/canonical website (`https://www.cynbit.in/`) and the portal (`https://portal.cynbit.in/`) return the HTTP header `Access-Control-Allow-Origin: *` on top-level HTML documents and 404 responses.

#### Evidence
HTTP response headers captured via curl:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Age: 228499
Cache-Control: public, max-age=0, must-revalidate
Content-Length: 100498
Content-Type: text/html; charset=utf-8
Server: Vercel
Strict-Transport-Security: max-age=63072000
```

#### Impact
1. While wildcard CORS is benign on truly static public media (images, fonts), emitting `Access-Control-Allow-Origin: *` globally across web application pages and internal portal routes exposes page content to cross-origin `fetch()` or `XMLHttpRequest` requests initiated by untrusted third-party websites.
2. If sensitive dynamic tokens, nonces, or user-specific states are rendered into HTML documents, malicious origins can read that data asynchronously.

#### Recommended Solution
1. Remove `Access-Control-Allow-Origin: *` from HTML document responses and dynamic application routes.
2. In FastAPI / Next.js backend middleware, restrict CORS headers to specific, authorized origins:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://cynbit.in", "https://www.cynbit.in", "https://portal.cynbit.in"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
       allow_headers=["Authorization", "Content-Type"],
   )
   ```

---

### FIND-004: Absence of Content Security Policy (CSP) Defense Header

- **Finding ID**: FIND-004
- **Category**: Web Application Security
- **Severity**: **Medium**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
No `Content-Security-Policy` (CSP) or `Content-Security-Policy-Report-Only` header was detected on any of the inspected routes (`https://www.cynbit.in/`, `https://www.cynbit.in/contact`, `https://portal.cynbit.in/`).

#### Evidence
Raw HTTP headers inspected across all public and portal endpoints return no `content-security-policy` field.

#### Impact
1. Content Security Policy is a foundational defense-in-depth mechanism recommended by OWASP. In the absence of a CSP, if an injection flaw occurs (e.g., via unescaped Markdown rendering in blog posts or third-party React components), the browser will execute arbitrary injected JavaScript.
2. Data exfiltration to attacker-controlled command-and-control servers cannot be blocked by browser network policies.

#### Recommended Solution
Configure a Content Security Policy header on edge responses:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://www.google-analytics.com; object-src 'none'; frame-ancestors 'none';
```

---

### FIND-005: Absence of Clickjacking Defense (`X-Frame-Options` / `frame-ancestors`)

- **Finding ID**: FIND-005
- **Category**: Web Application Security
- **Severity**: **Medium**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
Neither `X-Frame-Options` nor the CSP `frame-ancestors` directive is returned in response headers across Cynbit web properties.

#### Evidence
Header scan results on `https://www.cynbit.in/` and `https://portal.cynbit.in/`:
```http
X-Frame-Options: [NOT FOUND]
Content-Security-Policy: [NOT FOUND]
```

#### Impact
Without framing restrictions, an external adversary can embed the Cynbit portal or contact page inside an invisible `<iframe>` on an attacker-controlled website. By tricking authenticated users into clicking on decoy buttons aligned with portal controls, malicious actions (UI Redressing / Clickjacking) can be induced.

#### Recommended Solution
1. Add the following HTTP response header:
   ```http
   X-Frame-Options: DENY
   ```
2. Supplement with CSP directive:
   ```http
   Content-Security-Policy: frame-ancestors 'none';
   ```

---

### FIND-006: Missing `X-Content-Type-Options: nosniff` Header

- **Finding ID**: FIND-006
- **Category**: Web Application Security
- **Severity**: **Low**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
The HTTP response headers do not include `X-Content-Type-Options: nosniff`.

#### Evidence
Header inspection confirms the absence of `X-Content-Type-Options` on HTML and API responses.

#### Impact
Some browsers attempt to determine the content type of a file by inspecting its raw byte stream ("MIME sniffing") rather than honoring the server-provided `Content-Type` header. If user-submitted files (such as resume attachments on the careers page) are served without `nosniff`, an attacker might upload an HTML/SVG payload with a `.txt` or `.png` extension and trigger execution as script.

#### Recommended Solution
Enforce `X-Content-Type-Options: nosniff` across all edge and application server responses.

---

### FIND-007: Framework Fingerprinting via `X-Powered-By: Next.js`

- **Finding ID**: FIND-007
- **Category**: Information Disclosure
- **Severity**: **Low**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
Dynamic responses on the portal (such as the 307 redirect emitted when requesting `https://portal.cynbit.in/dashboard` without authentication) include the header `X-Powered-By: Next.js`.

#### Evidence
HTTP response from unauthenticated request to `/dashboard`:
```http
HTTP/1.1 307 Temporary Redirect
Location: /
Server: Vercel
Strict-Transport-Security: max-age=63072000
X-Matched-Path: /portal/dashboard
X-Powered-By: Next.js
X-Vercel-Cache: MISS
```

#### Impact
Disclosing specific framework technologies enables automated reconnaissance scanners to catalog the target stack and match known Common Vulnerabilities and Exposures (CVEs) related to specific Next.js releases.

#### Recommended Solution
Disable the banner in `next.config.js`:
```javascript
module.exports = {
  poweredByHeader: false,
};
```
In FastAPI backend implementations, ensure server banners like `server: uvicorn` are stripped or obscured via reverse proxy configuration.

---

### FIND-008: Administrative Route Enumeration via `robots.txt`

- **Finding ID**: FIND-008
- **Category**: Information Disclosure
- **Severity**: **Informational**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
The public `robots.txt` file explicitly lists internal paths to search engine crawlers:
```txt
User-agent: *
Allow: /

# Sitemap Location
Sitemap: https://cynbit.in/sitemap.xml

# Crawl Delay
Crawl-delay: 1

# Disallow specific non-SEO pages
Disallow: /api/
Disallow: /admin/
Disallow: /portal/
```

#### Impact
While intended to prevent search engines from indexing administrative pages, malicious reconnaissance tools parse `robots.txt` first. This explicitly informs attackers that `/portal/` and `/admin/` exist and should be targeted for authentication testing.

#### Recommended Solution
1. Do not use `robots.txt` as a substitute for access control.
2. Remove sensitive administrative path names from `robots.txt`.
3. Protect administrative interfaces using network firewalls, IP allowlists, or cloud access security brokers (e.g. Cloudflare Access, AWS Verified Access).

---

### FIND-009: Inconsistent SPF Records and Unenforced DMARC Policy (`p=none`)

- **Finding ID**: FIND-009
- **Category**: Email & Domain Security
- **Severity**: **Low**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
DNS queries reveal that Cynbit's primary MX record points to Microsoft 365 Outlook (`cynbit-in.mail.protection.outlook.com`). However, the domain's SPF record points only to GoDaddy/Secureserver (`v=spf1 include:secureserver.net -all`) and omits Microsoft's SPF mechanism. Furthermore, the DMARC policy is set to `p=none`.

#### Evidence
DNS records retrieved via `Resolve-DnsName`:
```txt
MX Record:
cynbit.in -> cynbit-in.mail.protection.outlook.com (Priority 0)

TXT Record (SPF):
cynbit.in -> "v=spf1 include:secureserver.net -all"

TXT Record (DMARC):
_dmarc.cynbit.in -> "v=DMARC1; p=none;"
```

#### Impact
1. **Deliverability Risks**: Outbound emails sent from Cynbit's official Microsoft 365 mailboxes may be flagged as spam or rejected by strict corporate mail servers because the sending IP (Microsoft) is not listed in the domain's SPF record.
2. **Email Spoofing Risks**: Because the DMARC policy is `p=none` (monitoring mode only), threat actors can send phishing emails with forged `@cynbit.in` sender addresses without receiving mail gateways rejecting the counterfeit emails.

#### Recommended Solution
1. Update the SPF TXT record:
   ```txt
   v=spf1 include:spf.protection.outlook.com include:secureserver.net -all
   ```
2. Upgrade DMARC policy from monitoring to enforcement:
   ```txt
   v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@cynbit.in; pct=100;
   ```

---

### FIND-010: Coupled Server Action Architecture Lacking Decoupled REST API Contract

- **Finding ID**: FIND-010
- **Category**: Backend Architecture
- **Severity**: **Informational**
- **Confidence Level**: Confirmed (High)
- **Status**: [OBSERVED]

#### Description
Inquiry and application forms are directly integrated into Next.js React Server Actions (`submitInquiry` and `submitCandidateApplication`) rather than communicating with an independent, documented RESTful API layer.

#### Evidence
Client-side form submission code from `contact/page-a581c8d7462124d9.js`:
```javascript
let x = (0, d.createServerReference)(
  "40247ba4465344b3386595bab4303317cdcce907df",
  d.callServer,
  void 0,
  d.findSourceMapURL,
  "submitInquiry"
);
let a = new FormData(e.currentTarget);
let r = await x(a);
```

#### Impact
1. **Tight Frontend-Backend Coupling**: Mutation logic, database transactions, and validation become deeply coupled with Next.js client component builds.
2. **Lack of Standard API Documentation**: No OpenAPI (Swagger) specifications exist for third-party integrations, external CRM synchronizations, or mobile clients.
3. **Validation & Error Handling Opacity**: When mutations fail, generic string messages ("Something went wrong") are returned to the client without structured error codes.

#### Recommended Solution
Design and deploy a standalone, decoupled REST API service (as demonstrated in our reference FastAPI implementation) offering:
- Clear OpenAPI/Swagger interactive documentation (`/docs`).
- Pydantic server-side validation models with granular validation error payloads.
- Structured HTTP response status codes (`201 Created`, `400 Bad Request`, `422 Unprocessable Entity`).
- Asynchronous database operations via SQLAlchemy and MySQL.

