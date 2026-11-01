import os
import re
import sys

def scan_codebase():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print("=" * 80)
    print("CYNBIT TECHNOLOGIES — STATIC CODE QUALITY & SECURITY AUDIT")
    print(f"Target Directory: {root_dir}")
    print("=" * 80)

    sql_patterns = [
        (r"execute\s*\(\s*f['\"].*\{.*\}['\"]\s*\)", "Raw f-string SQL query execution (SQL Injection risk)"),
        (r"execute\s*\(\s*['\"].*%s.*['\"]\s*%", "String-interpolated SQL query execution (SQL Injection risk)"),
        (r"text\s*\(\s*f['\"].*\{.*\}['\"]\s*\)", "f-string inside SQLAlchemy text() construct"),
    ]

    sensitive_patterns = [
        (r"(?i)(aws_access_key_id|aws_secret_access_key)\s*=\s*['\"][A-Za-z0-9/\+=]{20,}['\"]", "Hardcoded AWS credentials"),
        (r"(?i)private_key\s*=\s*['\"]-----BEGIN", "Hardcoded Private Key"),
    ]

    findings = []
    py_files_count = 0

    skip_dirs = {".git", ".pytest_cache", "__pycache__", "venv", ".venv", "alembic"}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude skip directories in place
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for fname in filenames:
            if fname.endswith(".py"):
                py_files_count += 1
                fpath = os.path.join(dirpath, fname)
                relpath = os.path.relpath(fpath, root_dir)

                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Check SQL patterns
                for pattern, desc in sql_patterns:
                    matches = re.finditer(pattern, content)
                    for m in matches:
                        line_no = content[:m.start()].count("\n") + 1
                        findings.append((relpath, line_no, desc, "High"))

                # Check sensitive credential patterns
                for pattern, desc in sensitive_patterns:
                    matches = re.finditer(pattern, content)
                    for m in matches:
                        line_no = content[:m.start()].count("\n") + 1
                        findings.append((relpath, line_no, desc, "Critical"))

    print(f"\n[1] Scanned {py_files_count} Python source files across app/, tests/, and scripts/.")

    if not findings:
        print("[PASS] Zero SQL injection vulnerabilities or hardcoded production secrets detected.")
    else:
        for relpath, line_no, desc, sev in findings:
            print(f"[{sev.upper()}] {relpath}:{line_no} - {desc}")

    # Check .gitignore rules
    print("\n[2] Checking .gitignore Coverage for Sensitive Files:")
    gitignore_path = os.path.join(root_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_content = f.read()
        for rule in [".env", "__pycache__", "*.db", ".pytest_cache"]:
            covered = rule in gi_content
            status = "[PASS]" if covered else "[FAIL]"
            print(f"  {status} Rule '{rule}' is present in .gitignore")
    else:
        print("  [FAIL] .gitignore is missing!")

    # Check Git tracked files for .env
    print("\n[3] Checking for Accidental Secret Files on Disk:")
    for sensitive_file in [".env", ".env.local", "id_rsa"]:
        exists = os.path.exists(os.path.join(root_dir, sensitive_file))
        status = "[WARN] Present on local disk (Ensure not committed!)" if exists else "[PASS] Absent (Protected)"
        print(f"  {status}: {sensitive_file}")

    print("\n" + "=" * 80)
    print("STATIC SECURITY AUDIT COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    scan_codebase()
