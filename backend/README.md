# StoreFlow Backend v2 — Authentication and Demo Reset

Production-readiness step for the StoreFlow forward-deployed inventory project.

## What changed from v1

- Bearer-token authentication
- Secure `scrypt` password hashing
- Signed HS256 access tokens with expiration
- Protected product, inventory, sales, reorder, analytics, and purchase-order APIs
- Seeded administrator account
- Admin-only demo reset endpoint
- Alembic migration for the `users` table
- Eight automated tests covering authentication and the full workflow
- Docker ports aligned with the current project: API `8001`, PostgreSQL `5434`

## Demo login

```text
Email:    admin@storeflow.demo
Password: StoreFlowDemo#2026Secure!
```

These credentials are intentionally included for a portfolio demo. Replace them and change `AUTH_SECRET_KEY` before a real production deployment.

## Start the backend

Stop the previous backend first from its terminal with `Control + C`, or from its folder:

```bash
docker compose down
```

Then run this version:

```bash
cd storeflow-backend-v2-auth
cp .env.example .env
docker compose up --build
```

The startup sequence will:

1. Start PostgreSQL on Mac port `5434`.
2. Apply the existing StoreFlow schema migration.
3. Apply the new users/authentication migration.
4. Seed the demo administrator.
5. Seed 4 suppliers, 48 products, 4,067 sales, and inventory adjustments.
6. Start FastAPI at `http://localhost:8001`.

Open:

- Swagger: `http://localhost:8001/docs`
- Health: `http://localhost:8001/health`

## Test login with curl

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@storeflow.demo","password":"StoreFlowDemo#2026Secure!"}'
```

The response includes `access_token`. In Swagger, open **Authorize** and paste:

```text
Bearer YOUR_ACCESS_TOKEN
```

The frontend handles this automatically.

## Protected routes

All business endpoints now require a valid bearer token:

```text
/api/v1/products
/api/v1/suppliers
/api/v1/inventory
/api/v1/sales
/api/v1/recommendations
/api/v1/purchase-orders
/api/v1/analytics
```

Public endpoints:

```text
GET  /health
POST /api/v1/auth/login
```

Authenticated account endpoint:

```text
GET /api/v1/auth/me
```

## Reset the portfolio demo

The administrator can restore all store data without deleting the login account:

```bash
curl -X POST http://localhost:8001/api/v1/demo/reset \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

The reset removes and recreates products, inventory, sales, recommendations, and purchase orders. Users remain intact.

## Tests

```bash
docker compose exec api pytest -q
```

Expected:

```text
8 passed
```

The suite covers:

- Public health endpoint
- Authentication requirement
- Successful and failed login
- Current-user endpoint
- Inventory updates
- CSV sales import and invalid barcode handling
- Reorder → purchase order → receiving workflow
- Admin demo reset while preserving users

## Important environment variables

```env
DATABASE_URL=postgresql+psycopg://storeflow:storeflow@db:5432/storeflow
AUTH_SECRET_KEY=replace-with-a-long-random-secret-before-production
ACCESS_TOKEN_MINUTES=480
DEMO_ADMIN_EMAIL=admin@storeflow.demo
DEMO_ADMIN_PASSWORD=StoreFlowDemo#2026Secure!
```

Generate a production secret with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Migration path from v1

When you run `alembic upgrade head`, Alembic applies:

```text
20260731_0001  Initial StoreFlow schema
20260731_0002  Add authenticated users
```

No manual SQL is required.
