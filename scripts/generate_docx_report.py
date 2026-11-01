import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_callout(doc, text, title=None, hex_bg="F0F4F8", hex_border="003366"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, hex_bg)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    # Left border only
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{hex_border}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    if title:
        run_title = p.add_run(f"{title}\n")
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(10.5)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(0, 51, 102)
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = RGBColor(45, 55, 72)
    
    # Spacing after callout table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def add_code_block(doc, code_str):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F8F9FA")
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="12" w:space="0" w:color="CBD5E0"/>'
        f'<w:top w:val="single" w:sz="12" w:space="0" w:color="CBD5E0"/>'
        f'<w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E0"/>'
        f'<w:right w:val="single" w:sz="12" w:space="0" w:color="CBD5E0"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(code_str)
    run.font.name = "Consolas"
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(33, 37, 41)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def style_heading(p, text, level=1):
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.bold = True
    if level == 1:
        run.font.size = Pt(17)
        run.font.color.rgb = RGBColor(0, 51, 102) # Navy
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(5)
    elif level == 2:
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0, 96, 103) # Teal
        p.paragraph_format.space_before = Pt(11)
        p.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(45, 55, 72)
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)

def add_body_paragraph(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(26, 32, 44)
    
    r_body = p.add_run(text)
    r_body.font.name = "Calibri"
    r_body.font.size = Pt(10.5)
    r_body.font.color.rgb = RGBColor(45, 55, 72)
    return p

def create_styled_table(doc, headers, data, col_widths=None, align_center_cols=None):
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], "003366")
        set_cell_margins(hdr_cells[i], top=100, bottom=100, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (align_center_cols and i in align_center_cols) else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        for r in p.runs:
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            r.font.bold = True
            r.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data rows
    for r_idx, row_data in enumerate(data):
        row_cells = tbl.rows[r_idx + 1].cells
        bg_col = "F7FAFC" if (r_idx % 2 == 1) else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if (align_center_cols and c_idx in align_center_cols) else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.05
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(45, 55, 72)
                
    # Table border styling
    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E0"/>'
        f'<w:left w:val="none"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="003366"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)
    
    if col_widths:
        for row in tbl.rows:
            for idx, width in enumerate(col_widths):
                row.cells[idx].width = Inches(width)
                
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)
    return tbl

def build_docx_report(output_path):
    doc = Document()
    
    # Set page margins to standard 1 inch
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)
        
    # ------------------ COVER PAGE ------------------
    cover_p0 = doc.add_paragraph()
    cover_p0.paragraph_format.space_before = Pt(36)
    cover_p0.paragraph_format.space_after = Pt(6)
    r_company = cover_p0.add_run("CYNBIT TECHNOLOGIES")
    r_company.font.name = "Calibri"
    r_company.font.size = Pt(14)
    r_company.font.bold = True
    r_company.font.color.rgb = RGBColor(0, 96, 103) # Teal
    
    cover_p1 = doc.add_paragraph()
    cover_p1.paragraph_format.space_before = Pt(6)
    cover_p1.paragraph_format.space_after = Pt(12)
    r_title = cover_p1.add_run("Backend Technical Audit Report &\nSystem Architecture Review")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0, 51, 102) # Navy
    
    cover_p2 = doc.add_paragraph()
    cover_p2.paragraph_format.space_before = Pt(4)
    cover_p2.paragraph_format.space_after = Pt(36)
    r_sub = cover_p2.add_run("Passive Observational Assessment, Security Evaluation, and Decoupled FastAPI Reference Backend")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(100, 116, 139)
    
    # Metadata card table on cover page
    meta_tbl = doc.add_table(rows=6, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_fields = [
        ("Candidate / Auditor:", "Chahat Modi"),
        ("Role Applied For:", "Backend Developer / Software Engineer (Assessment Submission)"),
        ("Academic Institution:", "JECRC University, Jaipur (Final-Year B.Tech CSE)"),
        ("Target Organization:", "Cynbit Technologies (Jaipur, Rajasthan, India)"),
        ("Audited Systems:", "https://cynbit.in/ (Canonical: www.cynbit.in) & portal.cynbit.in"),
        ("Date & Status:", "November 1, 2026 | Verified Complete (Version 1.0)"),
    ]
    for idx, (label, val) in enumerate(meta_fields):
        c0, c1 = meta_tbl.rows[idx].cells
        c0.width = Inches(2.2)
        c1.width = Inches(4.3)
        set_cell_background(c0, "F0F4F8")
        set_cell_background(c1, "F0F4F8")
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(1)
        p0.paragraph_format.space_after = Pt(1)
        r0 = p0.add_run(label)
        r0.font.name = "Calibri"
        r0.font.size = Pt(9.5)
        r0.font.bold = True
        r0.font.color.rgb = RGBColor(0, 51, 102)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r1 = p1.add_run(val)
        r1.font.name = "Calibri"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(45, 55, 72)
        
    # Border for metadata box
    tcPr = meta_tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="003366"/>'
        f'<w:left w:val="single" w:sz="8" w:space="0" w:color="003366"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="003366"/>'
        f'<w:right w:val="single" w:sz="8" w:space="0" w:color="003366"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tcPr.append(borders)
    
    doc.add_page_break()
    
    # ------------------ SECTION 1: EXECUTIVE SUMMARY ------------------
    p = doc.add_paragraph()
    style_heading(p, "1. Executive Summary", level=1)
    
    add_body_paragraph(
        doc,
        "This technical report presents a comprehensive backend audit and architectural analysis of Cynbit Technologies' "
        "publicly accessible digital ecosystem (https://cynbit.in/ and https://portal.cynbit.in/). As part of the Cynbit "
        "Backend Developer Technical Assessment, this investigation was conducted strictly adhering to passive, authorized, "
        "non-intrusive evaluation standards aligned with the OWASP Web Security Testing Guide (WSTG v4.2)."
    )
    
    add_callout(
        doc,
        "CORE AUDIT HIGHLIGHTS:\n"
        "• High Performance Edge: Hosted on Vercel Global Edge Network with Mumbai (BOM1) regional point of presence.\n"
        "• Modern Full-Stack Stack: Next.js App Router utilizing React Server Components (RSC) and Server Actions.\n"
        "• Strong Cryptographic Baseline: Enforces TLS 1.3 with AES-128-GCM and HSTS preload (63,072,000 seconds).\n"
        "• Authentication Vulnerability: Portal (portal.cynbit.in) uses single-factor shared password authentication ('Security Key') without username, email, or MFA.\n"
        "• Missing Defense Headers: Content-Security-Policy (CSP), X-Frame-Options, and X-Content-Type-Options are absent.\n"
        "• Architecture Decoupling Opportunity: Contact inquiries and candidate applications rely on coupled Next.js Server Actions rather than independent REST APIs.",
        title="Key Executive Observations"
    )
    
    add_body_paragraph(
        doc,
        "To demonstrate engineering best practices, a standalone reference backend architecture was designed and implemented "
        "using Python 3.11, FastAPI, MySQL 8.0, SQLAlchemy 2.x, Alembic, and JWT authentication. This reference implementation "
        "directly resolves the identified architectural and security shortcomings while demonstrating clean, modular backend engineering."
    )
    
    # ------------------ SECTION 2: SCOPE & METHODOLOGY ------------------
    p = doc.add_paragraph()
    style_heading(p, "2. Assessment Scope and Methodology", level=1)
    
    add_body_paragraph(
        doc,
        "The technical audit was executed across multiple network and application layers through passive observation:",
        bold_prefix="Multi-Tier Passive Methodology: "
    )
    
    methodology_items = [
        ("Layer 1: DNS & Domain Routing", "Inspection of A, MX, TXT (SPF), NS, and DMARC records via authoritative DNS resolvers."),
        ("Layer 2: Transport & Edge Infrastructure", "Direct TLS 1.3 socket negotiation, cipher inspection, certificate chain validation, and edge header analysis."),
        ("Layer 3: Application & Web Framework", "Next.js App Router routing patterns, Server-Side Rendering (SSR), Static Site Generation (SSG) caching, and robots.txt."),
        ("Layer 4: Data Handling & Server Actions", "Reverse engineering client JavaScript bundles for /contact, /careers, and /portal to uncover payload schemas and Server Actions."),
        ("Layer 5: Authentication & Session State", "Evaluation of administrative portal access flow, credential mechanisms, and client-side storage behaviors."),
    ]
    for lbl, desc in methodology_items:
        add_body_paragraph(doc, desc, bold_prefix=f"• {lbl}: ")
        
    add_callout(
        doc,
        "All audit statements throughout this report are classified strictly into four verified tiers:\n"
        "1. [OBSERVED]: Directly verified through HTTP response headers, script code, certificate exchange, or DNS responses.\n"
        "2. [INFERRED]: A logical, technical deduction based on visible architectural characteristics.\n"
        "3. [POTENTIAL RISK]: An engineering or security risk identified from observable configurations requiring internal review to confirm exploitability.\n"
        "4. [NOT VERIFIABLE]: An internal backend capability (e.g. database query parameters, indexing, server-side queues) that cannot be confirmed from external observation alone.",
        title="Evidence Classification Framework"
    )

    # ------------------ SECTION 3: WEBSITE ARCHITECTURE ------------------
    p = doc.add_paragraph()
    style_heading(p, "3. Website Architecture — Publicly Observable View", level=1)
    
    add_body_paragraph(
        doc,
        "Through passive network inspection, the external topography of Cynbit Technologies was mapped:"
    )
    
    arch_table_data = [
        ("Apex Domain", "https://cynbit.in/", "Resolves to Vercel Anycast IP 216.198.79.1. Emits HTTP 307 redirect to www."),
        ("Canonical Web URL", "https://www.cynbit.in/", "Primary public web presence; pre-rendered via Next.js App Router on Vercel."),
        ("Internal Portal", "https://portal.cynbit.in/", "Dedicated administrative portal subdomain; also redirected from /portal."),
        ("Edge Infrastructure", "Vercel BOM1 (Mumbai)", "Terminates TLS and serves static cached assets via edge CDN."),
        ("Email Infrastructure", "Microsoft 365 Exchange", "MX record: cynbit-in.mail.protection.outlook.com."),
    ]
    create_styled_table(
        doc,
        ["Component", "Network Target", "Observed Technical Architecture"],
        arch_table_data,
        col_widths=[1.5, 2.0, 3.0]
    )

    # ------------------ SECTION 4: API & SERVER ACTIONS ------------------
    p = doc.add_paragraph()
    style_heading(p, "4. API Behaviour and Structure", level=1)
    
    add_body_paragraph(
        doc,
        "Standard REST API discovery revealed that traditional endpoints such as /api or /api/v1 return an HTTP 404 page. "
        "Instead of exposing RESTful endpoints, Cynbit utilizes Next.js Server Actions (RPC-style asynchronous functions).",
        bold_prefix="Architectural Shift to Server Actions: "
    )
    
    server_actions_data = [
        ("submitInquiry", "40247ba4465344b3386595bab4303317cdcce907df", "/contact", "Accepts fullName, email, company, industry, message."),
        ("submitCandidateApplication", "40645a00e04f6854903cf3a65fda4c75ddd7691de9", "/careers/[slug]", "Accepts candidate metadata, serialized education JSON, and statement."),
        ("loginToPortal", "40d93da1cc26de4ef37bcb273184b7141ef77a50f8", "portal.cynbit.in/", "Processes single-field password authentication ('Security Key')."),
    ]
    create_styled_table(
        doc,
        ["Server Action Name", "Action Cryptographic Hash", "Page Origin", "Payload Scope"],
        server_actions_data,
        col_widths=[1.8, 2.2, 1.2, 1.3]
    )
    
    add_body_paragraph(
        doc,
        "Technical Implications: While Server Actions simplify React development by co-locating mutations with components, "
        "they introduce tight coupling between frontend builds and backend functions. They lack standardized OpenAPI/Swagger "
        "contracts, preventing third-party integrations, automated contract testing, or multi-platform client reuse.",
        bold_prefix="Engineering Trade-off: "
    )

    # ------------------ SECTION 5: DATA HANDLING & VALIDATION ------------------
    p = doc.add_paragraph()
    style_heading(p, "5. Data Handling and Input Validation", level=1)
    
    add_body_paragraph(
        doc,
        "De-obfuscation of the contact page bundle (contact/page-a581c8d7462124d9.js) demonstrates that client-side validation "
        "is limited to standard HTML5 input attributes: fullName (required), email (type=email, required), message (required). "
        "No explicit minLength or maxLength bounds are enforced in the client bundle."
    )
    
    add_code_block(
        doc,
        "// Extract from Cynbit Contact Bundle (page-a581c8d7462124d9.js):\n"
        "let x = (0, d.createServerReference)(\"40247ba4465344b3386595bab4303317cdcce907df\", d.callServer, void 0, d.findSourceMapURL, \"submitInquiry\");\n"
        "let a = new FormData(e.currentTarget);\n"
        "let r = await x(a);\n"
        "r.success ? i(!0) : n(\"Something went wrong. Please try again or email us directly.\");"
    )
    
    add_body_paragraph(
        doc,
        "Potential Backend Risk: If the server-side Server Action implementation lacks strict schema validation "
        "(e.g., Zod or Pydantic validation), malformed inputs, excessive payloads, or whitespace-only inputs can lead "
        "to unhandled server exceptions or database column truncation. A robust backend must never trust client-side validation alone."
    )

    # ------------------ SECTION 6: AUTHENTICATION AUDIT ------------------
    p = doc.add_paragraph()
    style_heading(p, "6. Authentication and Authorization", level=1)
    
    add_body_paragraph(
        doc,
        "Inspection of the Cynbit administrative portal (https://portal.cynbit.in/) uncovered several critical authentication design patterns:",
        bold_prefix="Portal Security Architecture: "
    )
    
    add_code_block(
        doc,
        "// Extract from Cynbit Portal Bundle (page-ba479285e84c64b5.js):\n"
        "let l = (0, s.createServerReference)(\"40d93da1cc26de4ef37bcb273184b7141ef77a50f8\", s.callServer, void 0, s.findSourceMapURL, \"loginToPortal\");\n"
        "async function c(r) {\n"
        "  r.preventDefault(), o(!0), s(\"\");\n"
        "  let t = new FormData();\n"
        "  t.append(\"password\", e);\n"
        "  let a = await l(t);\n"
        "  if (a.success) {\n"
        "    try { localStorage.setItem(\"cynbit_portal_last_activity\", Date.now().toString()); } catch (e) {}\n"
        "    window.location.href = \"/dashboard\";\n"
        "  } else { s(a.error || \"Login failed\"), o(!1); }\n"
        "}"
    )
    
    auth_eval_points = [
        ("Shared Single-Secret Risk", "The login form requires only a 'Security Key' (password). Because there is no username or email, all administrators share a single credential, eliminating non-repudiation and per-user audit trails."),
        ("No Multi-Factor Authentication", "Administrative access relies exclusively on this single secret without secondary verification (TOTP, WebAuthn)."),
        ("Insecure State Persistence", "Storing session activity in browser localStorage exposes session indicators to any script running within the origin."),
        ("Operational Route Guard", "Unauthenticated GET requests to /dashboard return an HTTP 307 redirect to /, confirming server-side route protection is active."),
    ]
    for lbl, desc in auth_eval_points:
        add_body_paragraph(doc, desc, bold_prefix=f"• {lbl}: ")

    # ------------------ SECTION 7: SECURITY OBSERVATIONS ------------------
    p = doc.add_paragraph()
    style_heading(p, "7. Security Observations & Header Matrix", level=1)
    
    headers_data = [
        ("Strict-Transport-Security", "Present (max-age=63072000)", "Compliant", "Enforces HTTPS preload for 2 years."),
        ("Content-Security-Policy (CSP)", "Missing", "Medium Risk", "No restrictions on script execution or exfiltration."),
        ("X-Frame-Options", "Missing", "Medium Risk", "Vulnerable to framing and Clickjacking attacks."),
        ("X-Content-Type-Options", "Missing", "Low Risk", "Allows browser MIME-sniffing on dynamic responses."),
        ("Access-Control-Allow-Origin", "Wildcard (*)", "Medium Risk", "Permissive CORS returned on top-level HTML documents."),
        ("X-Powered-By", "Exposed ('Next.js')", "Low Risk", "Reveals web framework identity and technology family."),
        ("DMARC Record", "p=none (Monitoring)", "Low Risk", "Does not enforce rejection or quarantine of spoofed emails."),
    ]
    create_styled_table(
        doc,
        ["Security Control", "Observed Configuration", "Severity", "Impact & Recommendation"],
        headers_data,
        col_widths=[1.8, 1.8, 1.1, 1.8],
        align_center_cols=[2]
    )

    # ------------------ SECTION 8: PERFORMANCE OBSERVATIONS ------------------
    p = doc.add_paragraph()
    style_heading(p, "8. Performance Observations", level=1)
    
    add_body_paragraph(
        doc,
        "Network telemetry demonstrates that Cynbit’s frontend performs efficiently for regional users due to Vercel’s "
        "Mumbai edge node (BOM1). Key performance assets include pre-rendered HTML (SSG), preloaded WOFF2 typography, "
        "and extracted Tailwind CSS chunks. However, canonical domain redirection from cynbit.in to www.cynbit.in uses "
        "HTTP 307 (Temporary) rather than HTTP 301 (Permanent), which prevents clients and search indexers from caching the canonical hop."
    )

    # ------------------ SECTION 9: ERROR HANDLING ------------------
    p = doc.add_paragraph()
    style_heading(p, "9. Error Handling & Observability", level=1)
    
    add_body_paragraph(
        doc,
        "Observed error responses on 404 pages and failed mutations are properly sanitized and do not leak database connection strings, "
        "file system paths, or execution stack traces. However, client-facing error responses are opaque ('Something went wrong'), "
        "which obscures actionable feedback during debugging. A production backend should return standardized, structured RFC 7807 problem details."
    )

    # ------------------ SECTION 10: FINDINGS REGISTER ------------------
    p = doc.add_paragraph()
    style_heading(p, "10. Comprehensive Findings Register", level=1)
    
    findings_summary_data = [
        ("FIND-001", "Auth & Access", "High", "Single-Factor Shared 'Security Key' Administrative Authentication"),
        ("FIND-002", "Session Mgmt", "Medium", "Client-Side Session Activity Storage in LocalStorage"),
        ("FIND-003", "Web Security", "Medium", "Permissive Wildcard Cross-Origin Resource Sharing on HTML Responses"),
        ("FIND-004", "App Security", "Medium", "Absence of Content Security Policy (CSP) Defense Header"),
        ("FIND-005", "App Security", "Medium", "Absence of Clickjacking Defense (X-Frame-Options / frame-ancestors)"),
        ("FIND-006", "App Security", "Low", "Missing X-Content-Type-Options: nosniff Header"),
        ("FIND-007", "Info Disclosure", "Low", "Framework Fingerprinting via X-Powered-By: Next.js"),
        ("FIND-008", "Info Disclosure", "Info", "Administrative Route Enumeration via robots.txt"),
        ("FIND-009", "Domain Security", "Low", "Inconsistent SPF Records and Unenforced DMARC Policy (p=none)"),
        ("FIND-010", "Architecture", "Info", "Coupled Server Action Architecture Lacking Decoupled REST API Contract"),
    ]
    create_styled_table(
        doc,
        ["Finding ID", "Category", "Severity", "Finding Title & Scope"],
        findings_summary_data,
        col_widths=[1.1, 1.3, 1.0, 3.1],
        align_center_cols=[0, 2]
    )

    # ------------------ SECTION 11: DETAILED FINDINGS ------------------
    p = doc.add_paragraph()
    style_heading(p, "11. Detailed Technical Findings & Remediation", level=1)
    
    detailed_findings = [
        ("FIND-001: Single-Factor Shared 'Security Key' Administrative Authentication",
         "Severity: High | Category: Authentication & Access Control | Confidence: Confirmed (High)\n\n"
         "Description: The administrative portal (portal.cynbit.in) uses a single password input ('Security Key') without username or email.\n"
         "Evidence: Observed in bundle page-ba479285e84c64b5.js (Server Action loginToPortal).\n"
         "Impact: Total lack of non-repudiation, impossibility of per-user audit logging, inability to revoke single user credentials, and absence of MFA.\n"
         "Remediation: Implement individual user accounts with bcrypt/argon2id password hashing, JWT authentication, and Role-Based Access Control (RBAC)."),
         
        ("FIND-002: Client-Side Session Activity Storage in LocalStorage",
         "Severity: Medium | Category: Session Management | Confidence: Confirmed (High)\n\n"
         "Description: Successful login writes timestamp to localStorage (cynbit_portal_last_activity).\n"
         "Evidence: Observed in bundle page-ba479285e84c64b5.js.\n"
         "Impact: HTML5 localStorage is accessible to any script running in the origin, exposing session metadata to XSS.\n"
         "Remediation: Manage session lifecycle on the server and use HttpOnly, Secure, SameSite=Strict cookies."),
         
        ("FIND-003: Permissive Wildcard Cross-Origin Resource Sharing on HTML Responses",
         "Severity: Medium | Category: Web Security & CORS | Confidence: Confirmed (High)\n\n"
         "Description: Both cynbit.in and portal.cynbit.in return Access-Control-Allow-Origin: * on top-level HTML documents.\n"
         "Evidence: Observed in raw curl HTTP response headers.\n"
         "Impact: Allows third-party scripts on external domains to perform cross-origin reads of HTML documents.\n"
         "Remediation: Restrict CORS exclusively to API endpoints and explicitly whitelisted origins."),
         
        ("FIND-004: Absence of Content Security Policy (CSP)",
         "Severity: Medium | Category: Web Application Security | Confidence: Confirmed (High)\n\n"
         "Description: No Content-Security-Policy header is configured across web properties.\n"
         "Evidence: Inspected HTTP response headers on public and portal routes.\n"
         "Impact: In the event of a client-side script injection flaw, the browser cannot block malicious script execution or data exfiltration.\n"
         "Remediation: Deploy a robust CSP defining script-src, style-src, connect-src, and frame-ancestors directives."),
         
        ("FIND-005: Absence of Clickjacking Defense",
         "Severity: Medium | Category: Web Application Security | Confidence: Confirmed (High)\n\n"
         "Description: X-Frame-Options and CSP frame-ancestors are missing from responses.\n"
         "Evidence: Inspected HTTP response headers.\n"
         "Impact: Attackers can embed Cynbit forms within transparent iframes on malicious sites to trick users into unauthorized clicks.\n"
         "Remediation: Enforce X-Frame-Options: DENY and Content-Security-Policy: frame-ancestors 'none'."),
         
        ("FIND-009: Inconsistent SPF and Unenforced DMARC Policy",
         "Severity: Low | Category: Email & Domain Security | Confidence: Confirmed (High)\n\n"
         "Description: MX points to Microsoft 365, SPF includes secureserver.net only, and DMARC is p=none.\n"
         "Evidence: Authoritative DNS resolution via Resolve-DnsName.\n"
         "Impact: Outbound emails may fail SPF validation at recipient gateways, and domain spoofing cannot be actively prevented.\n"
         "Remediation: Include spf.protection.outlook.com in SPF and upgrade DMARC to p=quarantine or p=reject."),
         
        ("FIND-010: Coupled Server Actions Lacking Decoupled REST API Contract",
         "Severity: Informational | Category: Backend Architecture | Confidence: Confirmed (High)\n\n"
         "Description: Inquiry handling is performed via Next.js Server Actions embedded within frontend bundles.\n"
         "Evidence: Discovered actions submitInquiry and submitCandidateApplication in page chunks.\n"
         "Impact: Prevents external service integration, mobile client reuse, and automated OpenAPI contract testing.\n"
         "Remediation: Build a standalone REST API service with FastAPI, Pydantic schemas, and Swagger documentation."),
    ]
    for title, content in detailed_findings:
        p_f = doc.add_paragraph()
        style_heading(p_f, title, level=2)
        add_callout(doc, content, hex_bg="FAFAFA", hex_border="006067")

    # ------------------ SECTION 12: EVIDENCE REGISTER ------------------
    p = doc.add_paragraph()
    style_heading(p, "12. Complete Evidence Register", level=1)
    
    evd_table_data = [
        ("EVD-001", "Routing", "307 redirect apex to www", "Observed", "SEO link equity loss", "Use 301 Permanent Redirect"),
        ("EVD-002", "Hosting", "Vercel Edge BOM1 (Mumbai)", "Observed", "Low regional latency", "Maintain edge caching"),
        ("EVD-003", "Framework", "Next.js App Router (RSC)", "Observed", "X-Powered-By exposed", "Disable poweredByHeader"),
        ("EVD-004", "CORS", "Wildcard Access-Control-Allow-Origin: *", "Observed", "Document data reading", "Restrict to trusted API origins"),
        ("EVD-005", "TLS Layer", "TLS 1.3, AES-128, Let's Encrypt", "Observed", "Strong transit security", "Maintain automated cert renewal"),
        ("EVD-006", "CSP", "No Content-Security-Policy header", "Observed", "Script injection risk", "Deploy strict CSP policy"),
        ("EVD-007", "Clickjacking", "Missing X-Frame-Options", "Observed", "UI redressing threat", "Add X-Frame-Options: DENY"),
        ("EVD-008", "MIME Sniff", "Missing X-Content-Type-Options", "Observed", "MIME-confusion risk", "Add X-Content-Type-Options: nosniff"),
        ("EVD-009", "Header Leak", "X-Powered-By: Next.js returned", "Observed", "Stack fingerprinting", "Strip framework banners"),
        ("EVD-010", "Robots.txt", "Disallow /api/, /admin/, /portal/", "Observed", "Attack surface disclosure", "Protect via WAF / network policy"),
        ("EVD-011", "Portal Host", "portal.cynbit.in returns 200 OK", "Observed", "Dedicated portal host", "Maintain host-level isolation"),
        ("EVD-012", "Portal Auth", "Single 'Security Key' password field", "Observed", "No non-repudiation / MFA", "Implement individual user JWT & RBAC"),
        ("EVD-013", "Session State", "localStorage cynbit_portal_last_activity", "Observed", "XSS accessible storage", "Use HttpOnly Secure cookies"),
        ("EVD-014", "Route Guard", "GET /dashboard yields 307 to /", "Observed", "Server guard operational", "Verify per-endpoint auth guards"),
        ("EVD-015", "Inquiry Form", "Server Action submitInquiry", "Observed", "Client HTML5 validation only", "Enforce strict Pydantic backend models"),
        ("EVD-016", "Careers Form", "submitCandidateApplication with JSON", "Observed", "Complex serialized input", "Validate JSON schema on server"),
        ("EVD-017", "Email Auth", "MX Outlook, SPF secureserver, DMARC p=none", "Observed", "Spoofing & delivery risks", "Update SPF for Outlook; set DMARC quarantine"),
        ("EVD-018", "Database", "Internal query engines & schema", "Not Verifiable", "Cannot be confirmed externally", "Use MySQL 8.0 with SQLAlchemy & Alembic"),
    ]
    create_styled_table(
        doc,
        ["ID", "Area", "Observation", "Class", "Risk Evaluation", "Recommendation"],
        evd_table_data,
        col_widths=[0.8, 1.0, 1.6, 0.9, 1.1, 1.1],
        align_center_cols=[0, 3]
    )

    # ------------------ SECTION 13: STRATEGIC ROADMAP ------------------
    p = doc.add_paragraph()
    style_heading(p, "13. Strategic Recommendations & Hardening Roadmap", level=1)
    
    roadmap_items = [
        ("Phase 1: Edge & DNS Hardening (Immediate)", "Convert apex redirect to 301 Permanent; update SPF record to include Microsoft Outlook; elevate DMARC policy to p=quarantine; disable poweredByHeader in next.config.js."),
        ("Phase 2: Security Headers & CORS Enforcement (Short-Term)", "Deploy Content-Security-Policy; set X-Frame-Options: DENY; set X-Content-Type-Options: nosniff; restrict CORS to trusted origins."),
        ("Phase 3: Identity & Access Management Overhaul (Medium-Term)", "Replace the single-key portal login with individual user accounts; hash passwords with bcrypt (work factor >= 12); enforce JWT access/refresh tokens with RBAC and optional TOTP MFA."),
        ("Phase 4: Decoupled REST Backend Architecture (Long-Term)", "Extract inquiry and applicant handling into a standalone FastAPI REST service with Pydantic validation, MySQL storage, SQLAlchemy ORM, and Alembic migrations."),
    ]
    for lbl, desc in roadmap_items:
        add_body_paragraph(doc, desc, bold_prefix=f"• {lbl}: ")

    # ------------------ SECTION 14: REFERENCE ARCHITECTURE ------------------
    p = doc.add_paragraph()
    style_heading(p, "14. Standalone Reference Backend Architecture", level=1)
    
    add_body_paragraph(
        doc,
        "To provide a tangible, production-grade model of the recommended decoupled architecture, a standalone "
        "Secure Inquiry Management API was architected using Python 3.11 and FastAPI:",
        bold_prefix="Reference Architecture Design: "
    )
    
    add_code_block(
        doc,
        "cynbit-backend-assessment/\n"
        "├── app/\n"
        "│   ├── main.py                     # FastAPI application factory & security middleware\n"
        "│   ├── core/\n"
        "│   │   ├── config.py               # Pydantic BaseSettings environment configuration\n"
        "│   │   ├── security.py             # bcrypt password hashing & PyJWT token management\n"
        "│   │   └── exceptions.py           # Global RFC 7807 structured exception handlers\n"
        "│   ├── database/\n"
        "│   │   ├── connection.py           # SQLAlchemy session engine & lifecycle\n"
        "│   │   └── base.py                 # Declarative Base for models\n"
        "│   ├── models/\n"
        "│   │   ├── inquiry.py              # Inquiry SQLAlchemy relational model\n"
        "│   │   └── admin.py                # AdminUser relational model with roles\n"
        "│   ├── schemas/\n"
        "│   │   ├── inquiry.py              # Pydantic models for validation & responses\n"
        "│   │   └── auth.py                 # Pydantic models for Login, Tokens & Users\n"
        "│   ├── routers/\n"
        "│   │   ├── inquiry.py              # Public inquiry creation & Protected admin CRUD\n"
        "│   │   └── auth.py                 # Login, profile, and token refresh endpoints\n"
        "│   ├── services/\n"
        "│   │   ├── inquiry_service.py      # Business logic & repository transactions\n"
        "│   │   └── auth_service.py         # Authentication verification & token issuance\n"
        "│   └── dependencies/\n"
        "│       └── auth.py                 # OAuth2 Bearer token verification & RBAC guard\n"
        "├── alembic/                        # Version-controlled schema migrations\n"
        "├── tests/                          # Automated Pytest + HTTPX test suite\n"
        "├── docs/                           # Technical audit reports, evidence & API documentation\n"
        "├── requirements.txt                # Locked application dependencies\n"
        "└── README.md                       # Comprehensive setup & architecture documentation"
    )

    # ------------------ SECTION 15: LIMITATIONS & ETHICS ------------------
    p = doc.add_paragraph()
    style_heading(p, "15. Limitations and Ethical Testing Statement", level=1)
    
    add_callout(
        doc,
        "ETHICAL COMPLIANCE DECLARATION:\n"
        "1. Strictly Non-Intrusive: All observations were gathered from publicly observable responses. No exploit payloads, SQL injections, or fuzzing attacks were transmitted.\n"
        "2. No Unauthorized Credential Access: No attempts were made to brute-force or guess Cynbit's portal 'Security Key'.\n"
        "3. Zero Data Modification: No form submissions were posted to Cynbit's production databases or recruitment teams.\n"
        "4. Observational Boundaries: Internal database schemas, serverless execution limits, and private CRM integrations are inherently unobservable from the outside and are classified accordingly as [NOT VERIFIABLE].",
        title="Ethical Testing Protocol"
    )

    # ------------------ SECTION 16: CONCLUSION & REFERENCES ------------------
    p = doc.add_paragraph()
    style_heading(p, "16. Conclusion and References", level=1)
    
    add_body_paragraph(
        doc,
        "Cynbit Technologies maintains a fast, aesthetically refined, edge-rendered digital platform leveraging modern Next.js "
        "and Vercel infrastructure. The observations documented in this audit present high-value, realistic engineering opportunities "
        "to elevate Cynbit's backend security and architectural maturity to enterprise standards. By replacing the shared single-key "
        "administrative authentication with individual JWT accounts, configuring missing defense-in-depth headers, and decoupling "
        "inquiry processing into a standalone FastAPI REST service, the platform will achieve robust resilience, strict non-repudiation, "
        "and scalable modularity."
    )
    
    ref_items = [
        ("OWASP Web Security Testing Guide (v4.2)", "WSTG-INFO-02 (Server Fingerprinting), WSTG-ATHN-01 (Credential Transport), WSTG-CONF-07 (HSTS)."),
        ("RFC 7519 Standards", "JSON Web Token (JWT) architecture, token expiration, and signature verification."),
        ("RFC 8446 Standards", "The Transport Layer Security (TLS) Protocol Version 1.3."),
        ("RFC 7807 Standards", "Problem Details for HTTP APIs (Structured Error Responses)."),
    ]
    for lbl, desc in ref_items:
        add_body_paragraph(doc, desc, bold_prefix=f"• {lbl}: ")
        
    doc.save(output_path)
    print(f"Document successfully created at: {output_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\Lenovo\Desktop\cynbit-backend-assesment\docs"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "Cynbit_Backend_Technical_Audit_Report.docx")
    build_docx_report(out_file)

