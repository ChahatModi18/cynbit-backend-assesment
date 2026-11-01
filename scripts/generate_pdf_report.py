import os
import fitz  # PyMuPDF

def generate_pdf(output_path):
    doc = fitz.open()
    
    # Color palette
    NAVY = (0/255, 51/255, 102/255)
    TEAL = (0/255, 96/255, 103/255)
    CHARCOAL = (45/255, 55/255, 72/255)
    MUTED = (100/255, 116/255, 139/255)
    LIGHT_BG = (240/255, 244/255, 248/255)
    CODE_BG = (248/255, 249/255, 250/255)
    BORDER_COL = (203/255, 213/255, 224/255)
    LINE_COL = (226/255, 232/255, 240/255)
    WHITE = (1, 1, 1)
    
    PAGE_WIDTH = 595.28  # A4 width in pt
    PAGE_HEIGHT = 841.89 # A4 height in pt
    MARGIN_LEFT = 54.0   # 0.75 in
    MARGIN_RIGHT = 54.0
    CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
    
    # ---------------- PAGE 1: COVER PAGE ----------------
    page1 = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    
    # Top decorative band
    page1.draw_rect(fitz.Rect(0, 0, PAGE_WIDTH, 14), color=None, fill=NAVY)
    page1.draw_rect(fitz.Rect(0, 14, PAGE_WIDTH, 20), color=None, fill=TEAL)
    
    # Company Header
    page1.insert_text((MARGIN_LEFT, 110), "CYNBIT TECHNOLOGIES", fontsize=15, fontname="helv", color=TEAL)
    
    # Title
    page1.insert_text((MARGIN_LEFT, 150), "Backend Technical Audit Report", fontsize=24, fontname="helv", color=NAVY)
    page1.insert_text((MARGIN_LEFT, 180), "& Architecture Review", fontsize=24, fontname="helv", color=NAVY)
    
    # Subtitle
    page1.insert_text((MARGIN_LEFT, 215), "Passive Observational Assessment, Security Evaluation, and Decoupled FastAPI Reference Backend", fontsize=10.5, fontname="tiit", color=MUTED)
    
    # Separator Line
    page1.draw_line(fitz.Point(MARGIN_LEFT, 235), fitz.Point(PAGE_WIDTH - MARGIN_RIGHT, 235), color=TEAL, width=2)
    
    # Overview Summary Box
    overview_rect = fitz.Rect(MARGIN_LEFT, 260, PAGE_WIDTH - MARGIN_RIGHT, 410)
    page1.draw_rect(overview_rect, color=BORDER_COL, fill=LIGHT_BG, width=1)
    page1.insert_text((MARGIN_LEFT + 15, 285), "Executive Overview & Audit Context", fontsize=12, fontname="hebo", color=NAVY)
    
    desc_lines = [
        "This formal technical document presents an external, non-intrusive backend technical audit",
        "of Cynbit Technologies' public digital web ecosystem (https://cynbit.in/ and portal.cynbit.in).",
        "Conducted as part of the Backend Developer Technical Assessment, this report evaluates",
        "API architecture, authentication posture, data validation patterns, edge caching behavior,",
        "and transport security in accordance with the OWASP Web Security Testing Guide (WSTG v4.2).",
        "",
        "The report includes a 10-point technical findings register, an 18-point classified evidence register,",
        "remediation roadmaps, and an architectural blueprint for a standalone production-grade reference",
        "backend built with Python 3.11, FastAPI, MySQL 8.0, SQLAlchemy 2.x, Alembic, and JWT."
    ]
    y_text = 308
    for line in desc_lines:
        if line:
            page1.insert_text((MARGIN_LEFT + 15, y_text), line, fontsize=9.5, fontname="tiro", color=CHARCOAL)
        y_text += 13
        
    # Metadata Card
    meta_rect = fitz.Rect(MARGIN_LEFT, 440, PAGE_WIDTH - MARGIN_RIGHT, 660)
    page1.draw_rect(meta_rect, color=NAVY, fill=WHITE, width=1.5)
    page1.draw_rect(fitz.Rect(MARGIN_LEFT, 440, PAGE_WIDTH - MARGIN_RIGHT, 465), color=None, fill=NAVY)
    page1.insert_text((MARGIN_LEFT + 15, 457), "AUDIT SPECIFICATION & METADATA", fontsize=10.5, fontname="hebo", color=WHITE)
    
    meta_rows = [
        ("Candidate / Lead Auditor:", "Chahat Modi"),
        ("Academic Institution:", "JECRC University, Jaipur (Final-Year B.Tech CSE)"),
        ("Role Applied For:", "Entry-Level Backend Developer / Software Engineer"),
        ("Target Organization:", "Cynbit Technologies (Jaipur, Rajasthan, India)"),
        ("Target Web Applications:", "https://cynbit.in/ (Canonical: www.cynbit.in) & portal.cynbit.in"),
        ("Hosting & Framework:", "Vercel Global Edge (Mumbai BOM1) | Next.js App Router (RSC)"),
        ("Audit Methodology:", "OWASP WSTG v4.2 Passive Observational & Transport Reconnaissance"),
        ("Assessment Date:", "November 1, 2026"),
        ("Submission Status:", "Final Verified Version 1.0"),
    ]
    my = 490
    for lbl, val in meta_rows:
        page1.insert_text((MARGIN_LEFT + 15, my), lbl, fontsize=9, fontname="hebo", color=NAVY)
        page1.insert_text((MARGIN_LEFT + 165, my), val, fontsize=9, fontname="tiro", color=CHARCOAL)
        page1.draw_line(fitz.Point(MARGIN_LEFT + 15, my + 5), fitz.Point(PAGE_WIDTH - MARGIN_RIGHT - 15, my + 5), color=LINE_COL, width=0.5)
        my += 18
        
    # Bottom footer on cover
    page1.insert_text((MARGIN_LEFT, 770), "CONFIDENTIAL TECHNICAL EVALUATION — PREPARED EXCLUSIVELY FOR CYNBIT TECHNOLOGIES", fontsize=8, fontname="helv", color=MUTED)
    page1.draw_rect(fitz.Rect(0, PAGE_HEIGHT - 10, PAGE_WIDTH, PAGE_HEIGHT), color=None, fill=NAVY)

    # ---------------- HELPER FOR SUBSEQUENT PAGES ----------------
    current_page_num = 1
    def create_content_page():
        nonlocal current_page_num
        current_page_num += 1
        p = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
        # Header
        p.insert_text((MARGIN_LEFT, 36), "CYNBIT TECHNOLOGIES — BACKEND TECHNICAL AUDIT REPORT", fontsize=8, fontname="hebo", color=MUTED)
        p.draw_line(fitz.Point(MARGIN_LEFT, 44), fitz.Point(PAGE_WIDTH - MARGIN_RIGHT, 44), color=BORDER_COL, width=0.75)
        # Footer
        p.draw_line(fitz.Point(MARGIN_LEFT, PAGE_HEIGHT - 38), fitz.Point(PAGE_WIDTH - MARGIN_RIGHT, PAGE_HEIGHT - 38), color=BORDER_COL, width=0.75)
        p.insert_text((MARGIN_LEFT, PAGE_HEIGHT - 25), "Chahat Modi | Entry-Level Backend Developer Submission", fontsize=8, fontname="tiro", color=MUTED)
        page_str = f"Page {current_page_num}"
        p.insert_text((PAGE_WIDTH - MARGIN_RIGHT - 35, PAGE_HEIGHT - 25), page_str, fontsize=8, fontname="helv", color=MUTED)
        return p

    # ---------------- PAGE 2: EXEC SUMMARY & SCOPE ----------------
    p2 = create_content_page()
    cy = 65
    
    p2.insert_text((MARGIN_LEFT, cy), "1. Executive Summary", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    exec_summary_text = [
        "A passive, non-intrusive backend technical audit of Cynbit Technologies' public digital infrastructure was",
        "conducted on November 1, 2026. The target surfaces comprise the primary website (https://cynbit.in/ and its",
        "canonical endpoint https://www.cynbit.in/) and the dedicated internal portal (https://portal.cynbit.in/).",
        "",
        "Key Engineering Highlights:",
        "1. Modern Edge Infrastructure: Cynbit utilizes the Vercel Global Edge Network with Mumbai (BOM1) termination,",
        "   achieving optimal regional latency for domestic visitors. Pre-rendered HTML assets exhibit high cache hit ratios.",
        "2. Modern Full-Stack Architecture: Next.js App Router powers the web application, leveraging React Server",
        "   Components (RSC) and Next.js Server Actions for state mutations.",
        "3. Cryptographic Transport Security: The platform enforces TLS 1.3 with AES-128-GCM cipher negotiation and an",
        "   automated Let's Encrypt certificate. HTTP Strict Transport Security (HSTS) is configured with a 2-year preload.",
        "4. Authentication Risk on Portal: The internal administrative portal utilizes a single-factor, shared 'Security Key'",
        "   password field without individual user accounts (no username/email) or multi-factor authentication (MFA).",
        "5. Missing Security Headers: The edge lacks defense-in-depth headers including Content-Security-Policy (CSP),",
        "   X-Frame-Options (Clickjacking defense), and X-Content-Type-Options: nosniff.",
        "6. Mutation Decoupling Opportunity: Contact inquiries and candidate applications rely on coupled Server Actions",
        "   rather than an independently documented, testable RESTful API with published OpenAPI/Swagger contracts."
    ]
    for line in exec_summary_text:
        if line:
            is_bold = line.startswith("Key Engineering") or line.startswith("1.") or line.startswith("2.") or line.startswith("3.") or line.startswith("4.") or line.startswith("5.") or line.startswith("6.")
            fnt = "hebo" if is_bold else "tiro"
            p2.insert_text((MARGIN_LEFT, cy), line, fontsize=9.2, fontname=fnt, color=CHARCOAL)
        cy += 13
        
    cy += 12
    p2.insert_text((MARGIN_LEFT, cy), "2. Assessment Scope and Methodology", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    scope_text = [
        "The technical audit adhered strictly to passive, authorized reconnaissance standards defined in the OWASP",
        "Web Security Testing Guide (WSTG v4.2). The scope encompassed five observational dimensions:",
        "• Network & DNS Layer: Authoritative queries for A, MX, TXT (SPF), NS, and DMARC records.",
        "• Transport & Cryptographic Layer: Direct TLS 1.3 socket negotiation, certificate chains, and HTTP security headers.",
        "• Application & Framework Layer: Next.js App Router routing patterns, SSG edge caching, and robots.txt paths.",
        "• Data Handling Layer: Client-side JavaScript bundle reverse engineering for /contact, /careers, and /portal.",
        "• Authentication & Session Layer: Verification of administrative credential flows and localStorage persistence."
    ]
    for line in scope_text:
        if line:
            p2.insert_text((MARGIN_LEFT, cy), line, fontsize=9.2, fontname="tiro", color=CHARCOAL)
        cy += 13
        
    cy += 15
    # Callout box for Evidence Classification
    box_rect = fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 130)
    p2.draw_rect(box_rect, color=BORDER_COL, fill=LIGHT_BG, width=1)
    p2.draw_rect(fitz.Rect(MARGIN_LEFT, cy, MARGIN_LEFT + 4, cy + 130), color=None, fill=NAVY)
    
    p2.insert_text((MARGIN_LEFT + 15, cy + 18), "EVIDENCE CLASSIFICATION FRAMEWORK", fontsize=10, fontname="hebo", color=NAVY)
    tiers = [
        ("[OBSERVED]: Directly verified through HTTP response headers, script code, certificate exchange, or DNS responses.", NAVY),
        ("[INFERRED]: A logical, technical deduction based on visible architectural patterns and framework behaviors.", TEAL),
        ("[POTENTIAL RISK]: An engineering risk identified from observable configurations requiring internal review to confirm.", (197/255, 48/255, 48/255)),
        ("[NOT VERIFIABLE]: An internal backend capability (e.g. database query parameters, indexing, server-side queues).", MUTED)
    ]
    ty = cy + 36
    for t_text, t_col in tiers:
        p2.insert_text((MARGIN_LEFT + 15, ty), t_text, fontsize=8.5, fontname="tiro", color=t_col)
        ty += 22

    # ---------------- PAGE 3: ARCHITECTURE & SERVER ACTIONS ----------------
    p3 = create_content_page()
    cy = 65
    
    p3.insert_text((MARGIN_LEFT, cy), "3. Website Architecture — Publicly Observable View", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    p3.insert_text((MARGIN_LEFT, cy), "Through passive network telemetry, the external hosting and edge topology was mapped:", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 15
    
    # Topology Table
    p3.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=None, fill=NAVY)
    p3.insert_text((MARGIN_LEFT + 10, cy + 12), "Component", fontsize=9, fontname="hebo", color=WHITE)
    p3.insert_text((MARGIN_LEFT + 130, cy + 12), "Network Target", fontsize=9, fontname="hebo", color=WHITE)
    p3.insert_text((MARGIN_LEFT + 280, cy + 12), "Observed Technical Architecture", fontsize=9, fontname="hebo", color=WHITE)
    cy += 18
    
    rows_p3 = [
        ("Apex Domain", "https://cynbit.in/", "Resolves to Vercel IP 216.198.79.1. Emits HTTP 307 to www."),
        ("Canonical URL", "https://www.cynbit.in/", "Primary public site; Next.js App Router on Vercel."),
        ("Internal Portal", "https://portal.cynbit.in/", "Dedicated portal subdomain; also redirected from /portal."),
        ("Edge Infrastructure", "Vercel BOM1 (Mumbai)", "Terminates TLS 1.3; serves cached SSG assets."),
        ("Email Infrastructure", "Microsoft 365 Exchange", "MX record: cynbit-in.mail.protection.outlook.com."),
    ]
    for c0, c1, c2 in rows_p3:
        p3.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=BORDER_COL, fill=WHITE, width=0.5)
        p3.insert_text((MARGIN_LEFT + 10, cy + 12), c0, fontsize=8.5, fontname="hebo", color=CHARCOAL)
        p3.insert_text((MARGIN_LEFT + 130, cy + 12), c1, fontsize=8.5, fontname="tiro", color=CHARCOAL)
        p3.insert_text((MARGIN_LEFT + 280, cy + 12), c2, fontsize=8.5, fontname="tiro", color=CHARCOAL)
        cy += 18
        
    cy += 20
    p3.insert_text((MARGIN_LEFT, cy), "4. API Behaviour and Structure (Next.js Server Actions)", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    p3.insert_text((MARGIN_LEFT, cy), "Standard API discovery indicated that traditional REST endpoints (/api, /api/v1) return HTTP 404 pages.", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 13
    p3.insert_text((MARGIN_LEFT, cy), "Instead, Cynbit utilizes Next.js Server Actions executed via client-server RPC references:", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 15
    
    # Server Actions Table
    p3.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=None, fill=NAVY)
    p3.insert_text((MARGIN_LEFT + 10, cy + 12), "Server Action Name", fontsize=9, fontname="hebo", color=WHITE)
    p3.insert_text((MARGIN_LEFT + 150, cy + 12), "Cryptographic Action Hash", fontsize=9, fontname="hebo", color=WHITE)
    p3.insert_text((MARGIN_LEFT + 360, cy + 12), "Page Origin", fontsize=9, fontname="hebo", color=WHITE)
    cy += 18
    
    actions_rows = [
        ("submitInquiry", "40247ba4465344b3386595bab4303317cdcce907df", "/contact"),
        ("submitCandidateApplication", "40645a00e04f6854903cf3a65fda4c75ddd7691de9", "/careers/[slug]"),
        ("loginToPortal", "40d93da1cc26de4ef37bcb273184b7141ef77a50f8", "portal.cynbit.in/"),
    ]
    for a0, a1, a2 in actions_rows:
        p3.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=BORDER_COL, fill=WHITE, width=0.5)
        p3.insert_text((MARGIN_LEFT + 10, cy + 12), a0, fontsize=8.5, fontname="cour", color=NAVY)
        p3.insert_text((MARGIN_LEFT + 150, cy + 12), a1, fontsize=8, fontname="cour", color=CHARCOAL)
        p3.insert_text((MARGIN_LEFT + 360, cy + 12), a2, fontsize=8.5, fontname="tiro", color=CHARCOAL)
        cy += 18
        
    cy += 16
    p3.insert_text((MARGIN_LEFT, cy), "Technical Assessment:", fontsize=10, fontname="hebo", color=NAVY)
    cy += 14
    eval_text = [
        "While Server Actions eliminate boilerplate for internal React mutations, they introduce tight coupling",
        "between frontend build artifacts and backend logic. They lack standardized OpenAPI/Swagger documentation,",
        "which restricts external integration, automated API fuzzing, and client reusability. In our reference build,",
        "we demonstrate how decoupling mutations into a standalone FastAPI REST API establishes clear contracts."
    ]
    for line in eval_text:
        p3.insert_text((MARGIN_LEFT, cy), line, fontsize=9.2, fontname="tiro", color=CHARCOAL)
        cy += 13

    # ---------------- PAGE 4: AUTH & SECURITY HEADERS ----------------
    p4 = create_content_page()
    cy = 65
    
    p4.insert_text((MARGIN_LEFT, cy), "5. Authentication & Administrative Portal Analysis", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    p4.insert_text((MARGIN_LEFT, cy), "De-obfuscation of the portal bundle (app/portal/page-ba479285e84c64b5.js) revealed the login routine:", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 14
    
    # Code snippet box
    code_rect = fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 90)
    p4.draw_rect(code_rect, color=BORDER_COL, fill=CODE_BG, width=1)
    code_lines = [
        "let l = (0, s.createServerReference)(\"40d93da1cc26de4ef37bcb273184b7141ef77a50f8\", s.callServer, ...);",
        "async function c(r) {",
        "  r.preventDefault(); let t = new FormData(); t.append(\"password\", e);",
        "  let a = await l(t);",
        "  if (a.success) {",
        "    try { localStorage.setItem(\"cynbit_portal_last_activity\", Date.now().toString()); } catch (e) {}",
        "    window.location.href = \"/dashboard\";",
        "  } else { s(a.error || \"Login failed\"); }",
        "}"
    ]
    k_y = cy + 14
    for cl in code_lines:
        p4.insert_text((MARGIN_LEFT + 12, k_y), cl, fontsize=8, fontname="cour", color=(33/255, 37/255, 41/255))
        k_y += 9.5
        
    cy += 105
    p4.insert_text((MARGIN_LEFT, cy), "Critical Authentication Findings:", fontsize=10, fontname="hebo", color=NAVY)
    cy += 14
    auth_points = [
        ("Shared Single-Secret Risk (FIND-001): ", "The portal accepts solely a 'Security Key' with no username/email. All admins share one secret, eliminating individual non-repudiation and per-user audit trails."),
        ("Absence of Multi-Factor Authentication: ", "No secondary authentication (TOTP/WebAuthn) is required for administrative entry."),
        ("Client-Side Storage Vulnerability (FIND-002): ", "Session activity is written to localStorage, which is accessible to any script executing within the origin (unlike HttpOnly cookies)."),
        ("Operational Route Guard (EVD-014): ", "Direct unauthenticated GET requests to /dashboard return an HTTP 307 redirect to /, verifying server-side route guards are operational.")
    ]
    for p_pre, p_desc in auth_points:
        p4.insert_text((MARGIN_LEFT, cy), p_pre, fontsize=8.8, fontname="hebo", color=NAVY)
        offset = len(p_pre) * 4.6
        p4.insert_text((MARGIN_LEFT + offset, cy), p_desc, fontsize=8.8, fontname="tiro", color=CHARCOAL)
        cy += 14
        
    cy += 12
    p4.insert_text((MARGIN_LEFT, cy), "6. Security Headers & CORS Analysis", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    # Headers Table
    p4.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=None, fill=NAVY)
    p4.insert_text((MARGIN_LEFT + 10, cy + 12), "Security Header / Policy", fontsize=9, fontname="hebo", color=WHITE)
    p4.insert_text((MARGIN_LEFT + 170, cy + 12), "Observed State", fontsize=9, fontname="hebo", color=WHITE)
    p4.insert_text((MARGIN_LEFT + 280, cy + 12), "Risk Severity", fontsize=9, fontname="hebo", color=WHITE)
    p4.insert_text((MARGIN_LEFT + 360, cy + 12), "Impact & Recommendation", fontsize=9, fontname="hebo", color=WHITE)
    cy += 18
    
    header_rows = [
        ("Strict-Transport-Security", "max-age=63072000", "Compliant", "Enforces HTTPS preload for 2 years."),
        ("Content-Security-Policy", "Missing", "Medium", "No script/connect source restrictions."),
        ("X-Frame-Options", "Missing", "Medium", "Susceptible to Clickjacking via iframes."),
        ("X-Content-Type-Options", "Missing", "Low", "Allows browser MIME-sniffing."),
        ("Access-Control-Allow-Origin", "Wildcard (*)", "Medium", "Permissive CORS on HTML documents."),
        ("X-Powered-By", "Next.js Exposed", "Low", "Reveals framework technology family."),
        ("DMARC Record", "p=none (Monitor)", "Low", "Does not reject or quarantine spoofed mail."),
    ]
    for h0, h1, h2, h3 in header_rows:
        p4.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 16), color=BORDER_COL, fill=WHITE, width=0.5)
        p4.insert_text((MARGIN_LEFT + 10, cy + 11), h0, fontsize=8.2, fontname="hebo", color=CHARCOAL)
        p4.insert_text((MARGIN_LEFT + 170, cy + 11), h1, fontsize=8.2, fontname="tiro", color=CHARCOAL)
        
        # Color badge for severity
        s_col = (197/255, 48/255, 48/255) if h2=="Medium" else (TEAL if h2=="Compliant" else MUTED)
        p4.insert_text((MARGIN_LEFT + 280, cy + 11), h2, fontsize=8.2, fontname="hebo", color=s_col)
        p4.insert_text((MARGIN_LEFT + 360, cy + 11), h3, fontsize=8, fontname="tiro", color=CHARCOAL)
        cy += 16

    # ---------------- PAGE 5: FINDINGS REGISTER ----------------
    p5 = create_content_page()
    cy = 65
    
    p5.insert_text((MARGIN_LEFT, cy), "7. Summary of Technical Findings", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    p5.insert_text((MARGIN_LEFT, cy), "The technical audit identified 10 distinct findings across authentication, security, and architecture:", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 15
    
    # Findings Table
    p5.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 18), color=None, fill=NAVY)
    p5.insert_text((MARGIN_LEFT + 10, cy + 12), "Finding ID", fontsize=9, fontname="hebo", color=WHITE)
    p5.insert_text((MARGIN_LEFT + 75, cy + 12), "Category", fontsize=9, fontname="hebo", color=WHITE)
    p5.insert_text((MARGIN_LEFT + 165, cy + 12), "Severity", fontsize=9, fontname="hebo", color=WHITE)
    p5.insert_text((MARGIN_LEFT + 235, cy + 12), "Finding Title & Scope", fontsize=9, fontname="hebo", color=WHITE)
    cy += 18
    
    findings_list = [
        ("FIND-001", "Auth & Access", "High", "Single-Factor Shared 'Security Key' Administrative Authentication"),
        ("FIND-002", "Session Mgmt", "Medium", "Client-Side Session Activity Storage in LocalStorage"),
        ("FIND-003", "Web Security", "Medium", "Permissive Wildcard Cross-Origin Resource Sharing on HTML Responses"),
        ("FIND-004", "App Security", "Medium", "Absence of Content Security Policy (CSP) Defense Header"),
        ("FIND-005", "App Security", "Medium", "Absence of Clickjacking Defense (X-Frame-Options / frame-ancestors)"),
        ("FIND-006", "App Security", "Low", "Missing X-Content-Type-Options: nosniff Header"),
        ("FIND-007", "Info Disclosure", "Low", "Framework Fingerprinting via X-Powered-By: Next.js"),
        ("FIND-008", "Info Disclosure", "Informational", "Administrative Route Enumeration via robots.txt"),
        ("FIND-009", "Domain Security", "Low", "Inconsistent SPF Records and Unenforced DMARC Policy (p=none)"),
        ("FIND-010", "Architecture", "Informational", "Coupled Server Action Architecture Lacking Decoupled REST API Contract"),
    ]
    for fid, cat, sev, title in findings_list:
        p5.draw_rect(fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 17), color=BORDER_COL, fill=WHITE, width=0.5)
        p5.insert_text((MARGIN_LEFT + 10, cy + 12), fid, fontsize=8.5, fontname="hebo", color=NAVY)
        p5.insert_text((MARGIN_LEFT + 75, cy + 12), cat, fontsize=8, fontname="tiro", color=CHARCOAL)
        
        s_col = (197/255, 48/255, 48/255) if sev=="High" else ((221/255, 107/255, 32/255) if sev=="Medium" else MUTED)
        p5.insert_text((MARGIN_LEFT + 165, cy + 12), sev, fontsize=8.5, fontname="hebo", color=s_col)
        p5.insert_text((MARGIN_LEFT + 235, cy + 12), title, fontsize=8.5, fontname="tiro", color=CHARCOAL)
        cy += 17
        
    cy += 20
    p5.insert_text((MARGIN_LEFT, cy), "8. Strategic Remediation Roadmap", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    phases = [
        ("Phase 1: Immediate Edge & DNS Hardening (Week 1)", "• Update SPF to include spf.protection.outlook.com.\n• Elevate DMARC to p=quarantine.\n• Disable poweredByHeader in next.config.js.\n• Convert apex redirect to HTTP 301 Permanent."),
        ("Phase 2: Security Header & CORS Enforcement (Week 2)", "• Implement Content-Security-Policy (CSP) with script nonces.\n• Enforce X-Frame-Options: DENY and X-Content-Type-Options: nosniff.\n• Restrict Access-Control-Allow-Origin strictly to trusted API origins."),
        ("Phase 3: Identity & Access Management Overhaul (Weeks 3-4)", "• Replace single security key with individual user accounts (email + password).\n• Hash passwords using bcrypt (work factor >= 12).\n• Issue signed JWT access/refresh tokens with RBAC (Admin, Staff, Auditor)."),
        ("Phase 4: Decoupled REST API Microservice (Weeks 5-6)", "• Extract inquiry and candidate workflows into a dedicated FastAPI REST API.\n• Enforce Pydantic schema validation on all inputs.\n• Persist records in MySQL 8.0+ managed via Alembic database migrations.")
    ]
    for ph_title, ph_desc in phases:
        p5.insert_text((MARGIN_LEFT, cy), ph_title, fontsize=9.5, fontname="hebo", color=TEAL)
        cy += 14
        for line in ph_desc.split("\n"):
            p5.insert_text((MARGIN_LEFT + 10, cy), line, fontsize=8.8, fontname="tiro", color=CHARCOAL)
            cy += 12
        cy += 5

    # ---------------- PAGE 6: REFERENCE BACKEND ARCHITECTURE ----------------
    p6 = create_content_page()
    cy = 65
    
    p6.insert_text((MARGIN_LEFT, cy), "9. Standalone Reference Backend Architecture", fontsize=15, fontname="hebo", color=NAVY)
    cy += 20
    
    p6.insert_text((MARGIN_LEFT, cy), "To provide Cynbit with a production-ready model addressing these audit findings, a standalone", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 13
    p6.insert_text((MARGIN_LEFT, cy), "Secure Inquiry Management API was architected using Python 3.11 and FastAPI:", fontsize=9.2, fontname="tiro", color=CHARCOAL)
    cy += 15
    
    # Directory Tree Box
    tree_rect = fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 220)
    p6.draw_rect(tree_rect, color=BORDER_COL, fill=CODE_BG, width=1)
    tree_lines = [
        "cynbit-backend-assessment/",
        "├── app/",
        "│   ├── main.py                     # FastAPI application factory & security middleware",
        "│   ├── core/",
        "│   │   ├── config.py               # Pydantic BaseSettings environment configuration",
        "│   │   ├── security.py             # bcrypt password hashing & PyJWT token management",
        "│   │   └── exceptions.py           # Global RFC 7807 structured exception handlers",
        "│   ├── database/",
        "│   │   ├── connection.py           # SQLAlchemy session engine & lifecycle",
        "│   │   └── base.py                 # Declarative Base for models",
        "│   ├── models/",
        "│   │   ├── inquiry.py              # Inquiry SQLAlchemy relational model",
        "│   │   └── admin.py                # AdminUser relational model with roles",
        "│   ├── schemas/",
        "│   │   ├── inquiry.py              # Pydantic models for validation & responses",
        "│   │   └── auth.py                 # Pydantic models for Login, Tokens & Users",
        "│   ├── routers/",
        "│   │   ├── inquiry.py              # Public inquiry creation & Protected admin CRUD",
        "│   │   └── auth.py                 # Login, profile, and token refresh endpoints",
        "│   ├── services/",
        "│   │   ├── inquiry_service.py      # Business logic & repository transactions",
        "│   │   └── auth_service.py         # Authentication verification & token issuance",
        "│   └── dependencies/",
        "│       └── auth.py                 # OAuth2 Bearer token verification & RBAC guard",
        "├── alembic/                        # Version-controlled schema migrations",
        "├── tests/                          # Automated Pytest + HTTPX test suite",
        "├── docs/                           # Technical audit reports, evidence & API documentation",
        "├── requirements.txt                # Locked application dependencies",
        "└── README.md                       # Comprehensive setup & architecture documentation"
    ]
    t_y = cy + 13
    for tl in tree_lines:
        p6.insert_text((MARGIN_LEFT + 10, t_y), tl, fontsize=7.5, fontname="cour", color=(33/255, 37/255, 41/255))
        t_y += 8.6
        
    cy += 235
    p6.insert_text((MARGIN_LEFT, cy), "Key Architectural Safeguards Implemented:", fontsize=10, fontname="hebo", color=NAVY)
    cy += 14
    safeguards = [
        ("• Decoupled REST Service: ", "Independent OpenAPI/Swagger documentation at /docs; testable by automated suites."),
        ("• Server-Side Pydantic Validation: ", "Sanitizes and enforces bounds on email, strings, lengths, and empty whitespace."),
        ("• Enterprise JWT Authentication: ", "Bcrypt password hashing (work factor >= 12), token expiration, and RBAC guards."),
        ("• Controlled Relational State: ", "MySQL 8.0 engine managed via SQLAlchemy 2.x and version-controlled Alembic migrations."),
        ("• Defense-in-Depth Middleware: ", "Global exception handling, strict CORS whitelisting, and secure response headers.")
    ]
    for s_pre, s_desc in safeguards:
        p6.insert_text((MARGIN_LEFT, cy), s_pre, fontsize=8.8, fontname="hebo", color=NAVY)
        offset = len(s_pre) * 4.6
        p6.insert_text((MARGIN_LEFT + offset, cy), s_desc, fontsize=8.8, fontname="tiro", color=CHARCOAL)
        cy += 13
        
    cy += 15
    # Ethical Declaration Box at bottom
    eth_rect = fitz.Rect(MARGIN_LEFT, cy, PAGE_WIDTH - MARGIN_RIGHT, cy + 60)
    p6.draw_rect(eth_rect, color=BORDER_COL, fill=LIGHT_BG, width=1)
    p6.insert_text((MARGIN_LEFT + 12, cy + 14), "ETHICAL TESTING DECLARATION", fontsize=9, fontname="hebo", color=NAVY)
    p6.insert_text((MARGIN_LEFT + 12, cy + 28), "All testing was strictly passive, external, and non-intrusive. No exploit payloads were sent, no credentials", fontsize=8.2, fontname="tiro", color=CHARCOAL)
    p6.insert_text((MARGIN_LEFT + 12, cy + 40), "were brute-forced, and zero data was submitted to Cynbit systems. Prepared with integrity by Chahat Modi.", fontsize=8.2, fontname="tiro", color=CHARCOAL)

    doc.save(output_path)
    print(f"PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\Lenovo\Desktop\cynbit-backend-assesment\docs"
    os.makedirs(out_dir, exist_ok=True)
    out_pdf = os.path.join(out_dir, "Cynbit_Backend_Technical_Audit_Report.pdf")
    generate_pdf(out_pdf)
