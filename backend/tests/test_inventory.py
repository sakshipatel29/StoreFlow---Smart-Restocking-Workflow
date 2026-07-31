def test_inventory_adjustment_changes_stock(client, seeded_store):
    before = client.get("/api/v1/inventory").json()
    assert before[0]["current_stock"] == 4

    response = client.post(
        "/api/v1/inventory/receive",
        json={"product_id": "PRD-001", "quantity": 12, "notes": "One case"},
    )
    assert response.status_code == 201

    after = client.get("/api/v1/inventory").json()
    assert after[0]["current_stock"] == 16
    assert after[0]["stock_status"] == "healthy"
