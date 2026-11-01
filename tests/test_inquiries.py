import pytest
from fastapi.testclient import TestClient
from app.models.inquiry import Inquiry


def test_create_inquiry_success(client: TestClient):
    """Verify that a customer can submit an inquiry publicly and receive a 201 Created."""
    payload = {
        "name": "Aarav Patel",
        "email": "aarav.patel@innovatetech.in",
        "company": "InnovateTech Labs",
        "subject": "Autonomous AI Agent Development",
        "message": "We would like to consult on architecting autonomous agentic pipelines for finance."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Aarav Patel"
    assert data["email"] == "aarav.patel@innovatetech.in"
    assert data["company"] == "InnovateTech Labs"
    assert data["status"] == "PENDING"
    assert "created_at" in data


def test_get_inquiry_by_id_authorized(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_reviewer: dict
):
    """Verify that an authenticated administrator can retrieve inquiry details including audit logs."""
    response = client.get(
        f"/api/v1/inquiries/{sample_inquiry.id}",
        headers=auth_headers_reviewer
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_inquiry.id
    assert data["email"] == sample_inquiry.email
    assert len(data["audit_logs"]) >= 1
    assert data["audit_logs"][0]["action"] == "CREATED"


def test_get_inquiry_by_id_unauthorized(client: TestClient, sample_inquiry: Inquiry):
    """Verify that unauthenticated access to inquiry details is rejected with 401."""
    response = client.get(f"/api/v1/inquiries/{sample_inquiry.id}")
    assert response.status_code == 401


def test_get_inquiry_by_id_not_found(client: TestClient, auth_headers_reviewer: dict):
    """Verify that querying a non-existent inquiry returns 404 with RFC 7807 structure."""
    response = client.get("/api/v1/inquiries/99999", headers=auth_headers_reviewer)
    assert response.status_code == 404
    data = response.json()
    assert data["title"] == "Resource Not Found"
    assert "does not exist" in data["detail"]


def test_list_inquiries_pagination(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_superadmin: dict
):
    """Verify that inquiry listing returns structured pagination metadata."""
    response = client.get("/api/v1/inquiries?page=1&page_size=10", headers=auth_headers_superadmin)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "pagination" in data
    pagination = data["pagination"]
    assert pagination["page"] == 1
    assert pagination["page_size"] == 10
    assert pagination["total_records"] >= 1
    assert isinstance(pagination["has_next"], bool)


def test_list_inquiries_filter_by_status(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_reviewer: dict
):
    """Verify filtering inquiries by lifecycle status."""
    # Query for PENDING
    res_pending = client.get("/api/v1/inquiries?status=PENDING", headers=auth_headers_reviewer)
    assert res_pending.status_code == 200
    items = res_pending.json()["items"]
    assert all(item["status"] == "PENDING" for item in items)

    # Query for RESOLVED (should be empty initially)
    res_resolved = client.get("/api/v1/inquiries?status=RESOLVED", headers=auth_headers_reviewer)
    assert res_resolved.status_code == 200
    assert len(res_resolved.json()["items"]) == 0


def test_list_inquiries_keyword_search(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_superadmin: dict
):
    """Verify keyword search across name, email, company, and subject."""
    # Search for "Logistics" (part of company name)
    res_found = client.get("/api/v1/inquiries?search=Logistics", headers=auth_headers_superadmin)
    assert res_found.status_code == 200
    assert len(res_found.json()["items"]) >= 1

    # Search for non-existent keyword
    res_empty = client.get("/api/v1/inquiries?search=NonExistentKeywordXYZ", headers=auth_headers_superadmin)
    assert res_empty.status_code == 200
    assert len(res_empty.json()["items"]) == 0


def test_update_inquiry_status_success(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_reviewer: dict
):
    """Verify that an administrator can update an inquiry's status and trigger an audit entry."""
    response = client.patch(
        f"/api/v1/inquiries/{sample_inquiry.id}/status",
        headers=auth_headers_reviewer,
        json={
            "status": "IN_REVIEW",
            "notes": "Assigned to solutions team for architecture discovery."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "IN_REVIEW"

    # Verify audit log was recorded
    detail_res = client.get(f"/api/v1/inquiries/{sample_inquiry.id}", headers=auth_headers_reviewer)
    audit_logs = detail_res.json()["audit_logs"]
    status_updates = [log for log in audit_logs if log["action"] == "STATUS_UPDATED"]
    assert len(status_updates) == 1
    assert status_updates[0]["old_status"] == "PENDING"
    assert status_updates[0]["new_status"] == "IN_REVIEW"


def test_update_inquiry_status_invalid_enum(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_reviewer: dict
):
    """Verify that invalid status values are rejected with 422."""
    response = client.patch(
        f"/api/v1/inquiries/{sample_inquiry.id}/status",
        headers=auth_headers_reviewer,
        json={"status": "INVALID_STATUS_VALUE"}
    )
    assert response.status_code == 422


def test_delete_inquiry_rbac_reviewer_forbidden(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_reviewer: dict
):
    """Verify that non-SuperAdmins (INQUIRY_REVIEWER) cannot delete inquiries (403 Forbidden)."""
    response = client.delete(
        f"/api/v1/inquiries/{sample_inquiry.id}",
        headers=auth_headers_reviewer
    )
    assert response.status_code == 403
    data = response.json()
    assert data["title"] == "Permission Denied"
    assert "SUPER_ADMIN" in data["detail"]


def test_delete_inquiry_rbac_superadmin_success(
    client: TestClient,
    sample_inquiry: Inquiry,
    auth_headers_superadmin: dict
):
    """Verify that a SUPER_ADMIN can delete an inquiry and its cascaded records."""
    response = client.delete(
        f"/api/v1/inquiries/{sample_inquiry.id}",
        headers=auth_headers_superadmin
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # Verify inquiry is gone
    verify_res = client.get(f"/api/v1/inquiries/{sample_inquiry.id}", headers=auth_headers_superadmin)
    assert verify_res.status_code == 404

