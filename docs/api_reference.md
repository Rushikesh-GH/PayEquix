# REST API Reference Manual

Interactive Swagger/OpenAPI documentation is served locally at:
`http://127.0.0.1:8000/docs`

---

## 1. Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/login`
Authenticates a user and returns a signed JWT access token.
- **Request Body:**
  ```json
  {
    "username": "admin",
    "password": "AdminPassword123!"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
    "token_type": "bearer",
    "user_id": "USR-ADMIN-01",
    "username": "admin",
    "role": "system_admin",
    "full_name": "System Administrator"
  }
  ```

---

## 2. System Endpoints (`/api/v1/system`)

### `GET /health`
Returns system health status.
- **Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "app_name": "Compensation Disparity Analysis System",
    "environment": "development"
  }
  ```

### `GET /api/v1/system/metrics`
Aggregated executive dashboard metrics.
- **Response (200 OK):**
  ```json
  {
    "total_employees": 5000,
    "valid_comparisons_count": 4995,
    "review_candidates_count": 142,
    "data_quality_exceptions_count": 5,
    "below_band_count": 28,
    "above_band_count": 45,
    "avg_compa_ratio": 0.9984
  }
  ```

---

## 3. Master Data (`/api/v1`)

### `GET /api/v1/employees`
Paginated search and filter for employees.
- **Query Parameters:** `search`, `role_id`, `level_id`, `location_id`, `status`, `page`, `page_size`.
- **Response (200 OK):**
  ```json
  {
    "total": 5000,
    "page": 1,
    "page_size": 25,
    "total_pages": 200,
    "items": [
      {
        "employee_id": "EMP-000001",
        "employee_code": "EC-000001",
        "first_name": "Aarav",
        "last_name": "Sharma",
        "role_id": "ROL-SWE",
        "role_name": "Software Engineer",
        "level_id": "LEV-IC3",
        "level_name": "Senior (IC3)",
        "location_id": "LOC-IN-BLR",
        "location_name": "Bangalore, India",
        "fte": 1.0,
        "hire_date": "2021-03-15",
        "employment_status": "active"
      }
    ]
  }
  ```

### `GET /api/v1/employees/{employee_id}/compensation-analysis`
Complete compensation parity breakdown with source-to-derived math traceability.
- **Response (200 OK):**
  ```json
  {
    "analysis": {
      "employee_id": "EMP-000001",
      "currency": "INR",
      "actual_base_salary": 2400000.0,
      "fte": 1.0,
      "reporting_currency": "USD",
      "exchange_rate": 0.0115,
      "normalized_fte_salary": 27600.0,
      "applicable_band_id": "BAND-SWE-IC3-IN-BLR-2026",
      "band_min": 22400.0,
      "band_mid": 28000.0,
      "band_max": 33600.0,
      "compa_ratio": 0.9857,
      "band_position": 46.43,
      "status": "VALID"
    }
  }
  ```

---

## 4. Proposals & Governance (`/api/v1/proposals`)

### `POST /api/v1/proposals`
Creates a draft compensation adjustment proposal. Requires `hr_partner` or `system_admin`.
- **Request Body:**
  ```json
  {
    "employee_id": "EMP-000001",
    "proposed_salary": 2600000.0,
    "proposed_currency": "INR",
    "reason_codes": "MARKET_PARITY",
    "evidence_summary": "Top 10% performance review rating; current compa-ratio below market peer median."
  }
  ```

### `POST /api/v1/proposals/{adjustment_id}/approve`
Approves proposal. **Separation of duties enforced:** proposal creator cannot approve their own submission (`HTTP 403 Forbidden`).

### `POST /api/v1/proposals/{adjustment_id}/apply`
Applies approved proposal. Creates a new `SalaryRecord` and an `AdjustmentApplicationEvent`. Bypassing approval returns `HTTP 400 Bad Request`.
