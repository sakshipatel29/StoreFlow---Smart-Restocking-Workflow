from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.sale import Sale
from app.services.sales import row_key


def test_recommendation_to_purchase_order_to_receiving(client, db_session, seeded_store):
    product = seeded_store["product"]
    start = datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc)
    for index in range(28):
        sold_at = start + timedelta(days=index)
        quantity = 2
        price = Decimal("2.50")
        db_session.add(
            Sale(
                product_id=product.id,
                sold_at=sold_at,
                quantity=quantity,
                unit_price=price,
                external_key=row_key(sold_at, product.barcode, quantity, price),
                source="TEST_HISTORY",
            )
        )
    db_session.commit()

    generate = client.post(
        "/api/v1/recommendations/generate",
        json={"history_days": 28, "review_cycle_days": 7},
    )
    assert generate.status_code == 200
    rec = generate.json()["recommendations"][0]
    assert rec["recommended_cases"] >= 1

    decision = client.patch(
        f"/api/v1/recommendations/{rec['id']}",
        json={"status": "ACCEPTED"},
    )
    assert decision.status_code == 200

    create_po = client.post("/api/v1/purchase-orders/from-recommendations")
    assert create_po.status_code == 201
    po_id = create_po.json()["created_order_ids"][0]

    approve = client.post(f"/api/v1/purchase-orders/{po_id}/approve")
    assert approve.status_code == 200
    assert approve.json()["status"] == "APPROVED"

    receive = client.post(f"/api/v1/purchase-orders/{po_id}/receive", json={})
    assert receive.status_code == 200
    assert receive.json()["status"] == "RECEIVED"

    inventory = client.get("/api/v1/inventory").json()
    assert inventory[0]["current_stock"] > 4
