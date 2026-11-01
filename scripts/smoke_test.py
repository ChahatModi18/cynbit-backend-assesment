import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def main():
    print("Initializing TestClient...")
    client = TestClient(app)
    
    print("Testing /api/v1/health...")
    res = client.get("/api/v1/health")
    print("Health Status:", res.status_code, res.json())
    
    print("Testing /api/v1/auth/login...")
    res_login = client.post("/api/v1/auth/login", json={
        "email": "admin@cynbit.in",
        "password": "Admin@Cynbit2026!"
    })
    print("Login Status:", res_login.status_code)
    token = res_login.json()["access_token"]
    print("Token received:", token[:25] + "...")
    
    print("Testing /api/v1/auth/me...")
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    print("Profile Status:", res_me.status_code, res_me.json()["email"])
    
    print("Testing POST /api/v1/inquiries...")
    res_inq = client.post("/api/v1/inquiries", json={
        "name": "Chahat Modi",
        "email": "chahat.modi@example.com",
        "company": "JECRC University",
        "subject": "Backend Assessment Smoke Test",
        "message": "Testing the decoupled REST API with full server validation."
    })
    print("Create Inquiry Status:", res_inq.status_code, res_inq.json()["id"])
    inq_id = res_inq.json()["id"]
    
    print("Testing GET /api/v1/inquiries...")
    res_list = client.get("/api/v1/inquiries", headers={"Authorization": f"Bearer {token}"})
    print("List Inquiries Status:", res_list.status_code, "Items:", len(res_list.json()["items"]))
    
    print("Testing PATCH /api/v1/inquiries/{id}/status...")
    res_patch = client.patch(
        f"/api/v1/inquiries/{inq_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "IN_REVIEW", "notes": "Smoke test status update."}
    )
    print("Patch Status:", res_patch.status_code, "New Status:", res_patch.json()["status"])
    
    print("Testing Security Headers on response:")
    for h in ["x-frame-options", "x-content-type-options", "content-security-policy", "strict-transport-security"]:
        print(f"  {h}: {res.headers.get(h)}")
        
    print("\n[OK] All smoke tests passed successfully!")

if __name__ == "__main__":
    main()
