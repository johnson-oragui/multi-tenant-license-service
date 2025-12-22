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

## API Endpoints

| Endpoint                            | Method | Description                                             |
| ----------------------------------- | ------ | ------------------------------------------------------- |
| `/licenses/provision/`              | POST   | Provision a license for a customer (US1)                |
| `/licenses/<license_key>/activate/` | POST   | Activate a license (US3)                                |
| `/licenses/<license_key>/`          | GET    | Check license status (US4)                              |
| `/licenses/by_email/`               | GET    | List all licenses for a given email across brands (US6) |

**OpenAPI/Swagger** is generated using `drf-spectacular`.
Endpoints support detailed request/response schemas with validation.

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

8. OpenAPI docs: `http://127.0.0.1:8000/api/schema/swagger-ui/`

---

## Known Limitations & Next Steps

- Seat management not fully implemented.
- LicenseKey reuse logic could be improved.
- Audit logging synchronous — could be async for scalability.
- US2 and US5 endpoints not yet implemented.
- CI caching for Docker layers could speed up builds.
- Production deployment (uWSGI + Kubernetes) configured but untested locally.
