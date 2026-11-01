# Cynbit Technologies — API Endpoint Reference Documentation

---

**Service**: Cynbit Technologies Secure Inquiry Management REST API  
**Base URL**: `http://127.0.0.1:8000/api/v1`  
**Interactive Swagger UI**: `http://127.0.0.1:8000/docs`  
**ReDoc Documentation**: `http://127.0.0.1:8000/redoc`  
**Authentication Scheme**: OAuth2 Bearer Token (JSON Web Tokens - RFC 7519)  
**Standard Response Format**: `application/json; charset=utf-8`  

---

## 1. Authentication Headers

All protected administrative endpoints require an HTTP `Authorization` header formatted as:
```http
Authorization: Bearer <jwt_access_token>
```
If the token is missing, expired, or cryptographically invalid, the API returns `401 Unauthorized`.

---

## 2. API Endpoints

### 2.1 System Health Check

#### `GET /api/v1/health`
Verifies that the FastAPI application and the database connection are operational.

- **Authentication**: None (Public)
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2026-11-01T10:45:00.123456Z"
}
```

---

### 2.2 Authentication Endpoints

#### `POST /api/v1/auth/login`
Authenticates an administrator with corporate email and password, issuing a signed JWT access token.

- **Authentication**: None (Public)
- **Rate Limiting**: Monitored for brute-force attempts.
- **Request Body (`application/json`)**:
```json
{
  "email": "admin@cynbit.in",
  "password": "SecureAdminPassword!2026"
}
```
- **Validation Rules**:
  - `email`: Valid email format, trimmed, lowercase.
  - `password`: Minimum 8 characters, non-empty.

- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "admin@cynbit.in",
    "full_name": "Lead Architect",
    "role": "SUPER_ADMIN",
    "is_active": true
  }
}
```

- **Error Responses**:
  - `401 Unauthorized`:
    ```json
    {
      "type": "https://errors.cynbit.in/unauthorized",
      "title": "Authentication Failed",
      "status": 401,
      "detail": "Invalid email or password."
    }
    ```
  - `422 Unprocessable Entity`: Input format error (e.g. invalid email structure).

---

#### `GET /api/v1/auth/me`
Retrieves the profile and role details of the currently authenticated administrator.

- **Authentication**: Bearer Token required
- **Response `200 OK`**:
```json
{
  "id": 1,
  "email": "admin@cynbit.in",
  "full_name": "Lead Architect",
  "role": "SUPER_ADMIN",
  "is_active": true,
  "last_login_at": "2026-11-01T10:30:00Z",
  "created_at": "2026-10-01T08:00:00Z"
}
```

---

### 2.3 Inquiry Management Endpoints

#### `POST /api/v1/inquiries`
Submits a new customer inquiry or business inquiry. This replaces the coupled Next.js Server Action with a clean REST API.

- **Authentication**: None (Public)
- **Request Body (`application/json`)**:
```json
{
  "name": "Rajesh Sharma",
  "email": "rajesh.sharma@example.com",
  "company": "Fintech Solutions India",
  "subject": "AI Workflow Automation Inquiry",
  "message": "We are seeking autonomous AI agent integration for our customer support and KYC pipeline."
}
```
- **Field Validation Rules**:
  - `name`: String, 2 to 100 characters. Automatically stripped of leading/trailing whitespace.
  - `email`: String, valid RFC 5322 email syntax, max 255 characters. Normalized to lowercase.
  - `company`: Optional string, max 100 characters.
  - `subject`: String, 3 to 150 characters. Non-empty.
  - `message`: String, 10 to 2000 characters. Rejects empty whitespace strings.

- **Response `201 Created`**:
```json
{
  "id": 101,
  "name": "Rajesh Sharma",
  "email": "rajesh.sharma@example.com",
  "company": "Fintech Solutions India",
  "subject": "AI Workflow Automation Inquiry",
  "message": "We are seeking autonomous AI agent integration for our customer support and KYC pipeline.",
  "status": "PENDING",
  "created_at": "2026-11-01T10:48:00Z",
  "updated_at": "2026-11-01T10:48:00Z"
}
```

- **Error Responses**:
  - `422 Unprocessable Entity`: Input validation error with field-specific diagnostics:
    ```json
    {
      "type": "https://errors.cynbit.in/validation-error",
      "title": "Validation Error",
      "status": 422,
      "detail": [
        {
          "loc": ["body", "email"],
          "msg": "value is not a valid email address",
          "type": "value_error"
        }
      ]
    }
    ```

---

#### `GET /api/v1/inquiries`
Retrieves a paginated list of submitted inquiries with optional status filtering and full-text keyword search.

- **Authentication**: Bearer Token required (Any active administrator)
- **Query Parameters**:
  - `page` (`integer`, optional, default `1`): Page number ($\ge 1$).
  - `page_size` (`integer`, optional, default `20`): Items per page ($1 \le \text{page\_size} \le 100$).
  - `status` (`string`, optional): Filter by enum (`PENDING`, `IN_REVIEW`, `CONTACTED`, `RESOLVED`, `ARCHIVED`).
  - `search` (`string`, optional): Case-insensitive keyword search across `name`, `email`, `company`, and `subject`.

- **Response `200 OK`**:
```json
{
  "items": [
    {
      "id": 101,
      "name": "Rajesh Sharma",
      "email": "rajesh.sharma@example.com",
      "company": "Fintech Solutions India",
      "subject": "AI Workflow Automation Inquiry",
      "message": "We are seeking autonomous AI agent integration...",
      "status": "PENDING",
      "created_at": "2026-11-01T10:48:00Z",
      "updated_at": "2026-11-01T10:48:00Z"
    }
  ],
  "pagination": {
    "total_records": 1,
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

---

#### `GET /api/v1/inquiries/{id}`
Retrieves a single inquiry by its unique database ID.

- **Authentication**: Bearer Token required
- **Path Parameter**: `id` (`integer`, required)
- **Response `200 OK`**: Complete `InquiryResponse` object.
- **Error Response `404 Not Found`**:
```json
{
  "type": "https://errors.cynbit.in/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Inquiry with ID 999 does not exist."
}
```

---

#### `PATCH /api/v1/inquiries/{id}/status`
Updates an inquiry's lifecycle status and logs the administrative mutation into `inquiry_audit_logs`.

- **Authentication**: Bearer Token required (Any active administrator)
- **Path Parameter**: `id` (`integer`, required)
- **Request Body (`application/json`)**:
```json
{
  "status": "IN_REVIEW",
  "notes": "Assigned to solutions engineering team for discovery call."
}
```
- **Allowed Status Transitions**:
  - `PENDING` -> `IN_REVIEW`, `CONTACTED`, `RESOLVED`, `ARCHIVED`
  - `IN_REVIEW` -> `CONTACTED`, `RESOLVED`, `ARCHIVED`
  - `CONTACTED` -> `RESOLVED`, `ARCHIVED`
  - `RESOLVED` -> `ARCHIVED`

- **Response `200 OK`**: Updated `InquiryResponse` object.
- **Error Responses**:
  - `400 Bad Request`: Invalid status value.
  - `404 Not Found`: Inquiry does not exist.

---

#### `DELETE /api/v1/inquiries/{id}`
Permanently deletes an inquiry record. Enforces Role-Based Access Control: only administrators with role `SUPER_ADMIN` are authorized.

- **Authentication**: Bearer Token required (`SUPER_ADMIN` role required)
- **Path Parameter**: `id` (`integer`, required)
- **Response `200 OK`**:
```json
{
  "success": true,
  "message": "Inquiry 101 successfully deleted."
}
```
- **Error Responses**:
  - `403 Forbidden`: Raised when an `INQUIRY_REVIEWER` attempts deletion:
    ```json
    {
      "type": "https://errors.cynbit.in/forbidden",
      "title": "Insufficient Permissions",
      "status": 403,
      "detail": "Action requires SUPER_ADMIN privilege."
    }
    ```
  - `404 Not Found`: Inquiry does not exist.

---

## 3. Standard HTTP Status Code Reference

| Code | Meaning | Context in Cynbit Reference Backend |
|---|---|---|
| `200 OK` | Request Succeeded | Returned for successful GET, PATCH, and DELETE operations. |
| `201 Created` | Resource Created | Returned upon successful creation of an inquiry via `POST /api/v1/inquiries`. |
| `400 Bad Request` | Client Error | Malformed status transition or unparseable JSON syntax. |
| `401 Unauthorized` | Authentication Failed | Missing or invalid Bearer JWT token, or incorrect login credentials. |
| `403 Forbidden` | Access Denied | Authenticated user lacks the requisite role (e.g. non-superadmin attempting DELETE). |
| `404 Not Found` | Resource Absent | Requested inquiry ID does not exist in the database. |
| `422 Unprocessable Entity` | Validation Failure | Pydantic schema rejection (invalid email, too short, empty string). |
| `500 Internal Server Error` | Server Exception | Centralized error handler catches unexpected errors without exposing stack traces. |

