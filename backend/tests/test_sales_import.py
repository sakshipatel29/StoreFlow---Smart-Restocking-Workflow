def test_csv_import_updates_inventory_and_rejects_unknown_barcode(client, seeded_store):
    csv_data = """sold_at,barcode,quantity,unit_price
2026-07-31T10:00:00,111111111111,2,2.50
2026-07-31T10:05:00,999999999999,1,1.00
"""
    response = client.post(
        "/api/v1/sales/import",
        files={"file": ("sales.csv", csv_data, "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["rows_imported"] == 1
    assert body["rows_rejected"] == 1

    inventory = client.get("/api/v1/inventory").json()
    assert inventory[0]["current_stock"] == 2
