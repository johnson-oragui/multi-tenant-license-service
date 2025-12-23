## Problem and Requirements

This project implements a **Centralized License Service** for multiple brands and WordPress products.

**Core requirements addressed:**

1. Brands can provision licenses for customers.
2. End-user products can activate and check license status.
3. Support for multi-brand, multi-product licensing with a single source of truth.
4. Observability and audit logging of all license actions.
5. Clear API endpoints for provisioning, activation, and license queries.

**Minimum Implementation (Core Slice):**

- US1: License provisioning
- US3: License activation
- US4: License status query
- US6: List licenses by customer email

Optional:

- Audit logging is included.
- Rate-limiting and schema validation implemented.

---

## Architecture and Design

**High-Level Architecture:**

```
+----------------+          +---------------------+
| Brand Systems  | <--API--> | License Service     |
| (WP Rocket,    |          | (Django REST API)  |
|  RankMath, ...) |          | License Key &      |
+----------------+          | License DB         |
                            | Audit Logs         |
                            +---------------------+
                                  ^
                                  |
                            +------------+
                            | PostgreSQL |
                            +------------+
```

**Key Design Points:**

- **Multi-tenancy:** Brands, products, and customers are separate tables with proper foreign key relationships.
- **LicenseKey model:** A single key can unlock multiple licenses for a customer across a brand.
- **Audit logging:** All license operations log events for observability.
- **API layer:** DRF APIViews with serializers; OpenAPI/Swagger schema via `drf-spectacular`.
- **UUIDv7 for PKs:** Sequential, unique, and generated in Python before insertion.

**Core Models:**

- `Brand`: Represents a brand.
- `Product`: Represents a product belonging to a brand.
- `Customer`: Represents a customer email.
- `LicenseKey`: Represents a key that can unlock multiple licenses.
- `License`: Represents an entitlement to a product.
- `AuditLog`: Records all significant actions.

**Transactions:**

- `provision_license()` runs inside a single atomic transaction using `transaction.atomic()`.
- Guarantees consistency between license creation and audit logging.
- Future evolution: audit logs could be asynchronously written via message queues.

---

## Trade-offs and Decisions

**UUIDv7 vs AutoField**

- Chose UUIDv7 for sequential PKs, globally unique, and decoupled from DB.
- Alternative: DB auto-increment integer. Rejected for multi-database scaling and migration ease.

**Audit Logging**

- Current implementation writes logs in the same transaction as license creation (strong consistency).
- Alternative: async/outbox pattern for high-scale decoupling.
- Decision: synchronous logging suffices for MVP and assessment scope.

**LicenseKey Uniqueness**

- Currently, each provisioning creates a new key.
- Alternative: reuse existing key per brand/customer to unlock multiple products.
- Decision: Implemented as-is; noted in documentation for potential improvement.

**Transactions**

- All core license operations are wrapped in `transaction.atomic()` to ensure rollback on errors.

---

## Observability & Operations

- **Audit logs:** Capture actor, action, target, and metadata.
- **Rate-limiting:** Simple per-IP/brand throttling via Django DRF throttles.
- **OpenAPI/Swagger:** For testing and client integration.
- **CI/CD:** GitHub Actions pipeline:

  - Linting (`pylint`, `black`, `isort`)
  - Unit tests (`pytest` with coverage)
  - Dockerized PostgreSQL for integration testing
  - Artifact upload for coverage reports

---

## How the Solution Satisfies User Stories

| User Story                              | Status           | Notes                                        |
| --------------------------------------- | ---------------- | -------------------------------------------- |
| US1: Brand can provision license        | ✅ Implemented   | Single transaction, audit logging included   |
| US2: Brand can change license lifecycle | ⚪ Designed-only | Methods and API planned, not yet implemented |
| US3: End-user can activate license      | ✅ Implemented   | DRF endpoint with seat management optional   |
| US4: User can check license status      | ✅ Implemented   | Returns active licenses and entitlements     |
| US5: Deactivate seat                    | ⚪ Designed-only | Planned using activation table               |
| US6: List licenses by email             | ✅ Implemented   | Only accessible by brand systems             |

---

## Setup Instructions

1. Clone the repository.
2. Create virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements/dev.txt
   ```

4. Copy `.env`:

   ```bash
   cp env.sample .env
   ```

5. Run migrations:

   ```bash
   python -m manage migrate
   ```

6. Run tests:

   ```bash
   pytest --cov=. --cov-report=xml --cov-report=term
   ```

7. Run development server:

   ```bash
   python -m manage runserver
   ```

8. OpenAPI docs: `http://127.0.0.1:8000/api/docs/`

---

## Known Limitations & Next Steps

- Seat management not fully implemented.
- LicenseKey reuse logic could be improved.
- Audit logging synchronous — could be async for scalability.
- CI caching for Docker layers could speed up builds.
- Production deployment (uWSGI + Kubernetes) configured but untested locally.

---

## API Endpoints

| Feature                         | Endpoint                                   | Method | Auth          | Description                                             |
| ------------------------------- | ------------------------------------------ | ------ | ------------- | ------------------------------------------------------- |
| Brand Signup                    | `/api/v1/auth/brands/signup/`              | POST   | None          | Create a new brand and get API key                      |
| License Provision               | `/api/v1/licenses/`                        | POST   | Brand API key | Provision license for customer email                    |
| License Validate & Activate     | `/api/v1/licenses/validate/`               | POST   | None          | Validate license key and activate on an instance        |
| License Status                  | `/api/v1/licenses/status/`                 | POST   | None          | Check license status, entitlements, and remaining seats |
| License Deactivate              | `/api/v1/licenses/deactivate/`             | POST   | None          | Deactivate a specific activation (free a seat)          |
| License Suspend                 | `/api/v1/licenses/<license_id>/suspend/`   | POST   | Brand API key | Suspend a license temporarily                           |
| License Revoke                  | `/api/v1/licenses/<license_id>/revoke/`    | POST   | Brand API key | Revoke a license permanently                            |
| License Reinstate               | `/api/v1/licenses/<license_id>/reinstate/` | POST   | Brand API key | Reinstate a suspended license                           |
| List Licenses by Customer Email | `/api/v1/licenses/email-listing/`          | POST   | Brand API key | List all licenses for a customer across brands          |

**OpenAPI/Swagger** is generated using `drf-spectacular`.
Endpoints support detailed request/response schemas with validation.

---

## Example Requests / Responses

### 1. Brand Signup

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/brands/signup/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{
  "name": "string"
}'
```

**Response**

```json
{
	"message": "string",
	"success": true,
	"data": {
		"id": "string",
		"api_key": "string",
		"name": "string"
	}
}
```

### 2. Provision License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{
  "product_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "customer_email": "user@example.com",
  "expires_at": "2025-12-23T14:50:08.838Z"
}'
```

**Response**

```json
{
	"message": "License provisioned successfully.",
	"success": true,
	"data": {
		"license_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
		"license_key": "string",
		"status": "active",
		"expires_at": "2025-12-23T14:50:13.198Z"
	}
}
```

### 3. Reinstate License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/11111111-1111-1111-1111-111111111111/reinstate/' \
  -H 'accept: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d ''
```

**Response**

```json
{
	"message": "License successfully Reinstated",
	"success": true
}
```

### 4. Revoke License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/11111111-1111-1111-1111-111111111111/revoke/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"reason": "string"}'
```

**Response**

```json
{
	"message": "License successfully Revoked",
	"success": true
}
```

### 5. Suspend License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/11111111-1111-1111-1111-111111111111/suspend/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"reason": "string", "deactivate_existing": false}'
```

**Response**

```json
{
	"message": "License successfully suspended",
	"success": true
}
```

### 6. Deactivate License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/deactivate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"license_key": "string", "product_code": "string", "instance_identifier": "string"}'
```

**Response**

```json
{
	"message": "License successfully deactivated",
	"success": true
}
```

### 7. List Licenses by Customer Email

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/email-listing/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"customer_email": "user@example.com"}'
```

**Response**

```json
{
	"message": "Licenses retrieved successfully",
	"success": true,
	"data": [
		{
			"license_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
			"license_key": "string",
			"brand": { "id": "string", "name": "string" },
			"product": { "id": "string", "code": "string", "name": "string" },
			"status": "string",
			"expires_at": "2025-12-23T14:53:13.293Z",
			"is_active": true,
			"active_seats": 0
		}
	]
}
```

### 8. License Status

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/status/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"license_key": "string"}'
```

**Response**

```json
{
	"message": "string",
	"success": true,
	"data": {
		"entitlements": [
			{
				"product_code": "string",
				"status": "string",
				"expires_at": "2025-12-23T14:53:39.555Z",
				"seat_limit": 0,
				"active_seats": 0,
				"remaining_seats": 0
			}
		],
		"license_key": "string",
		"customer_email": "user@example.com",
		"valid": true
	}
}
```

### 9. Validate & Activate License

```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/licenses/validate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'X-CSRFTOKEN: <csrftoken>' \
  -d '{"license_key": "string", "product_code": "string", "instance_identifier": "string"}'
```

**Response**

```json
{
	"message": "License provisioned successfully.",
	"success": true,
	"data": {
		"license_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
		"license_key": "string",
		"status": "active",
		"expires_at": "2025-12-23T14:54:08.987Z"
	}
}
```
