# API workflow map

## Customer action: upload sales

`POST /api/v1/sales/import`

Server actions:

1. Validate UTF-8 CSV and required columns.
2. Match every barcode to the product catalog.
3. Generate deterministic row keys.
4. Reject unknown or malformed rows.
5. Skip duplicate rows and duplicate files.
6. Insert sales.
7. Insert matching negative inventory transactions.
8. Commit the import atomically.

## Customer action: review suggested order

`POST /api/v1/recommendations/generate`

Server actions:

1. Read the latest available sales date.
2. Calculate 28-day velocity by product.
3. Calculate current stock from the inventory ledger.
4. Subtract units already on open purchase orders.
5. Round required units to supplier case packs.
6. Save an explanation with every recommendation.

## Customer action: approve weekly order

1. `PATCH /api/v1/recommendations/{id}`
2. `POST /api/v1/purchase-orders/from-recommendations`
3. `POST /api/v1/purchase-orders/{id}/approve`

Accepted recommendations are grouped by supplier. A separate purchase order is created for each supplier.

## Customer action: receive delivery

`POST /api/v1/purchase-orders/{id}/receive`

The server records positive inventory transactions linked to the purchase order and marks the order received when every item is complete.
