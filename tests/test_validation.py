import pytest
from fastapi.testclient import TestClient


def test_validation_missing_name(client: TestClient):
    """Verify that omitting the required 'name' field returns 422."""
    payload = {
        "email": "user@example.com",
        "subject": "Missing Name Test",
        "message": "Testing that missing name raises schema validation error."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422
    assert response.json()["title"] == "Validation Error"


def test_validation_missing_email(client: TestClient):
    """Verify that omitting the required 'email' field returns 422."""
    payload = {
        "name": "Test User",
        "subject": "Missing Email Test",
        "message": "Testing that missing email raises schema validation error."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_invalid_email_syntax(client: TestClient):
    """Verify that invalid email strings are rejected."""
    invalid_emails = [
        "notanemail",
        "@missingusername.com",
        "username@.com",
        "user name@example.com",
        "user@domain..com"
    ]
    for bad_email in invalid_emails:
        payload = {
            "name": "Test User",
            "email": bad_email,
            "subject": "Email Syntax Test",
            "message": "Testing that bad email syntax raises validation error."
        }
        response = client.post("/api/v1/inquiries", json=payload)
        assert response.status_code == 422, f"Failed to reject invalid email: {bad_email}"


def test_validation_whitespace_only_name(client: TestClient):
    """Verify that whitespace-only name strings are strictly rejected."""
    payload = {
        "name": "     ",
        "email": "user@example.com",
        "subject": "Whitespace Name Test",
        "message": "Testing whitespace only name rejection."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_whitespace_only_message(client: TestClient):
    """Verify that whitespace-only message strings are strictly rejected."""
    payload = {
        "name": "Test User",
        "email": "user@example.com",
        "subject": "Whitespace Message Test",
        "message": "               "
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_name_too_short(client: TestClient):
    """Verify that single-character names (< 2 chars) are rejected."""
    payload = {
        "name": "A",
        "email": "user@example.com",
        "subject": "Short Name Test",
        "message": "Testing that single character names are rejected."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_name_too_long(client: TestClient):
    """Verify that names exceeding 100 characters are rejected."""
    payload = {
        "name": "A" * 101,
        "email": "user@example.com",
        "subject": "Long Name Test",
        "message": "Testing that oversized names are rejected."
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_message_too_short(client: TestClient):
    """Verify that messages shorter than 10 characters are rejected."""
    payload = {
        "name": "Valid User",
        "email": "user@example.com",
        "subject": "Short Message Test",
        "message": "Hi"
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_message_too_long(client: TestClient):
    """Verify that messages exceeding 2000 characters are rejected."""
    payload = {
        "name": "Valid User",
        "email": "user@example.com",
        "subject": "Long Message Test",
        "message": "M" * 2001
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 422


def test_validation_automatic_whitespace_trimming(client: TestClient):
    """Verify that valid inputs with surrounding whitespace are cleaned and accepted."""
    payload = {
        "name": "   Siddharth Verma   ",
        "email": "   siddharth@example.com   ",
        "company": "   Verma Industries   ",
        "subject": "   Automation Inquiry   ",
        "message": "   This is a valid inquiry message with leading and trailing spaces.   "
    }
    response = client.post("/api/v1/inquiries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Siddharth Verma"
    assert data["email"] == "siddharth@example.com"
    assert data["company"] == "Verma Industries"
    assert data["subject"] == "Automation Inquiry"
    assert data["message"] == "This is a valid inquiry message with leading and trailing spaces."


def test_validation_pagination_bounds(client: TestClient, auth_headers_reviewer: dict):
    """Verify that query parameters outside bounds raise 422 validation errors."""
    # page=0 is invalid (must be >= 1)
    res_page_zero = client.get("/api/v1/inquiries?page=0", headers=auth_headers_reviewer)
    assert res_page_zero.status_code == 422

    # page_size=0 is invalid (must be >= 1)
    res_size_zero = client.get("/api/v1/inquiries?page_size=0", headers=auth_headers_reviewer)
    assert res_size_zero.status_code == 422

    # page_size=101 is invalid (must be <= 100)
    res_size_large = client.get("/api/v1/inquiries?page_size=101", headers=auth_headers_reviewer)
    assert res_size_large.status_code == 422

