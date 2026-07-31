# StoreFlow Step 4 — Secure Full-Stack Demo

This package adds authentication, user sessions, demo-reset support, and automated integration tests to the PostgreSQL-backed StoreFlow workflow.

## 1. Stop the older versions

In the terminals running the old backend and frontend, press:

```text
Control + C
```

From the old backend folder, also run:

```bash
docker compose down
```

## 2. Start Backend v2

```bash
cd backend
cp .env.example .env
docker compose up --build
```

Wait until the log shows:

```text
Uvicorn running on http://0.0.0.0:8000
```

The API is exposed to your Mac at:

```text
http://localhost:8001
```

## 3. Start Frontend v3

Open a second terminal:

```bash
cd frontend
python3 -m http.server 4173
```

Open:

```text
http://localhost:4173
```

## 4. Sign in

```text
Email:    admin@storeflow.demo
Password: StoreFlow123!
```

## 5. Validate the complete workflow

1. Sign in and confirm the dashboard loads.
2. Open Inventory, record a `-1` adjustment, then refresh the page.
3. Open Sales Import, use the demo import, and send valid rows to FastAPI.
4. Generate reorder recommendations.
5. Accept or modify at least one recommendation.
6. Create supplier purchase orders.
7. Approve and receive one purchase order.
8. Return to Inventory and confirm stock increased.
9. Export the purchase order CSV.
10. Select **Reset demo data** and confirm the original dataset returns.
11. Sign out and confirm protected screens are no longer visible.

## 6. Run automated backend tests

From the project root while Docker is running:

```bash
cd backend
docker compose exec api pytest -q
```

Expected:

```text
8 passed
```

## Important

The included account is only for a portfolio demo. Before deployment, replace `AUTH_SECRET_KEY`, `DEMO_ADMIN_EMAIL`, and `DEMO_ADMIN_PASSWORD` in `.env`.
