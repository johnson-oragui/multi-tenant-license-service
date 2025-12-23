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
| List Licenses by Customer Email | `/api/v1/licenses/list/`     | GET    | Brand API key | List all licenses for a customer across brands          |

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
GET /api/v1/licenses/list/?limit=10&offset=0
```

---

## Utils

* `Util.hash_value` / `Util.verify_hash` → HMAC-SHA256 API key hashing.
* Safe JSON serialization and obfuscation for logging.

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


