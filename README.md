# Multi-Tenant License Service

A Django-based backend service for managing multi-tenant software licenses. This service allows brands to provision licenses, manage license lifecycle, and enables end-users to activate, deactivate, and check license status.

---

## Features / User Stories

### US1: Brand can provision a license

* Brands can generate **license keys** and create **licenses** for customer emails.
* A single license key can unlock multiple products for a customer.
* Each license tracks:

  * Product
  * Status (`valid`, `suspended`, `cancelled`)
  * Expiration date

### US2: Brand can change license lifecycle

* Brands can **renew**, **suspend/resume**, or **revoke** licenses.

### US3: End-user product can activate a license

* End-users can activate a license for a specific instance (e.g., machine ID or site URL).
* Activation enforces seat limits when applicable.

### US4: User can check license status

* End-users can check license validity, entitlements, and remaining seats.

### US5: End-user or customer can deactivate a seat

* Free a seat by deactivating a license activation.

### US6: Brands can list licenses by customer email

* Retrieve all licenses associated with a customer email across all brands.
* **Access restricted** to brands only.

---

## Project Structure

```
.
├── common/                    # Shared utilities and pagination schema
├── config/                    # Django configuration
│   ├── settings/              # Environment-specific settings
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── docker/                    # Docker-related files
│   └── app/                   # Dockerfile & entrypoint scripts
├── licenses/                  # License management app
│   ├── authentication.py      # Brand API key auth
│   ├── middleware.py          # Request/response logging
│   ├── models.py
│   ├── serializers.py
│   ├── services.py            # License business logic
│   ├── tests/                 # End-to-end and unit tests
│   └── urls.py, views.py
├── requirements/              # Python dependencies
├── manage.py
├── pyproject.toml
├── uwsgi.ini
└── docker-compose.yaml
```

---

## Environment Setup

### 1. Clone the repository

```bash
git clone https://github.com/johnson-oragui/multi-tenant-license-service
cd multi-tenant-license-service/license-service
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # Linux / macOS
```

### 3. Install dependencies

```bash
pip install -r requirements/dev.txt
```

### 4. Environment variables

Create a `.env` file based on `env.sample`:

```dotenv
PORT=8000
SECRET_KEY=some-secret
DJANGO_ALLOWED_HOSTS=*
DJANGO_SETTINGS_MODULE=config.settings.ci
DATABASE_URL="postgres://postgres:postgres@localhost:5432/license_service"
API_KEY_HMAC_SECRET="some-api-key-hmac-secret"
```

> For production, set secure `SECRET_KEY`.

---

## Docker Setup

### Build Docker image

```bash
docker-compose build
```

### Run service

```bash
docker-compose up
```

### Dockerfile paths

* `docker/app/Dockerfile` → Production
* `docker/app/dev.Dockerfile` → Development
* `docker/app/entrypoint.sh` → Entrypoint

---

## API Endpoints

| Feature                         | Endpoint                                   | Method | Auth          | Description                                             |
| ------------------------------- | ------------------------------------------ | ------ | ------------- | ------------------------------------------------------- |
| Brand Signup                    | `/api/v1/brands/signup/`                   | POST   | None          | Create a new brand and get API key                      |
| License Provision               | `/api/v1/licenses/`                        | POST   | Brand API key | Provision license for customer email                    |
| License Validate & Activate     | `/api/v1/licenses/validate/`               | POST   | None          | Validate license key and activate on an instance        |
| License Status                  | `/api/v1/licenses/status/`                 | POST   | None          | Check license status, entitlements, and remaining seats |
| License Deactivate              | `/api/v1/licenses/deactivate/`             | POST   | None          | Deactivate a specific activation (free a seat)          |
| License Suspend                 | `/api/v1/licenses/<license_id>/suspend/`   | POST   | Brand API key | Suspend a license temporarily                           |
| License Revoke                  | `/api/v1/licenses/<license_id>/revoke/`    | POST   | Brand API key | Revoke a license permanently                            |
| License Reinstate               | `/api/v1/licenses/<license_id>/reinstate/` | POST   | Brand API key | Reinstate a suspended license                           |
| List Licenses by Customer Email | `/api/v1/licenses/email-listing/`     | GET    | Brand API key | List all licenses for a customer across brands          |

---

## Authentication

* Brands authenticate using `X-API-KEY` header.
* API keys are **hashed** using HMAC-SHA256 before storage for security.
* Example header:

```http
X-API-KEY: <brand-api-key>
```

---

## License Lifecycle & Activations

* Each license has `status` and `expires_at`.
* Activation model tracks **instance-specific activations**.
* Enforces **idempotent activations** and **seat limits**.
* Audit logging is included for all license operations.

---

## Logging / Observability

* Middleware logs request/response cycles to console:

  * Correlation ID
  * Actor type (`brand` / `user` / `system`)
  * Brand ID / User ID
  * HTTP method, path, status code
  * Duration
  * Request / response payloads (sensitive data obfuscated)
* All license actions are logged in `AuditLog`.

---

## Testing

### Run tests

```bash
pytest
```

### Features tested

* Brand signup
* License provisioning
* License lifecycle operations (suspend, revoke, reinstate)
* License activation/deactivation
* License status retrieval
* List licenses by customer email
* Pagination and seat limit enforcement

---

## Pagination

* List endpoints use `LimitOffsetPagination`.
* Query parameters:

  * `limit` → number of items
  * `offset` → starting index
* Example:

```http
GET /api/v1/licenses/email-listing/?limit=10&offset=0
```

---

## Utils

* `Util.hash_value` / `Util.verify_hash` → HMAC-SHA256 API key hashing.
* Safe JSON serialization and obfuscation for logging.

---

--mple Requests / Responses

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
---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

---

## License

MIT License

---


