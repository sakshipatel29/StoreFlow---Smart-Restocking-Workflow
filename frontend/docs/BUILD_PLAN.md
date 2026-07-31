# StoreFlow Build Plan

## Step 1 — Frontend workflow prototype (included)

Goal: demonstrate the entire user journey before backend implementation.

Completed workflow:

```text
Sales CSV → Validation → Inventory update → Reorder recommendations
→ Owner decisions → Supplier purchase orders → Approval → Receiving
```

## Step 2 — FastAPI backend

Build these modules in order:

1. Project configuration and health endpoint
2. PostgreSQL connection
3. Supplier and product models
4. Inventory transaction ledger
5. Sales-import validation and idempotency
6. Reorder service
7. Purchase-order service
8. Authentication and store scoping
9. Tests and Docker Compose

## Step 3 — Connect frontend to API

Replace localStorage operations with an API client while keeping the same screens.

Suggested endpoints:

```text
GET    /api/products
POST   /api/products
PATCH  /api/products/{id}
GET    /api/inventory
POST   /api/inventory/adjustments
POST   /api/inventory/receipts
POST   /api/sales/import
POST   /api/recommendations/generate
GET    /api/recommendations
PATCH  /api/recommendations/{id}
POST   /api/purchase-orders
POST   /api/purchase-orders/{id}/approve
POST   /api/purchase-orders/{id}/receive
```

## Step 4 — Production readiness

- User authentication
- Store and role permissions
- Structured logging
- Database migrations
- Retry-safe imports
- Error monitoring
- CI/CD
- Cloud deployment

## Step 5 — Real store pilot

Pilot one category and supplier for two or three weekly order cycles. Measure:

- Weekly ordering time
- Products missed during manual checks
- Recommendation acceptance rate
- Stockouts
- Inventory-count accuracy
- Dead or expired inventory
