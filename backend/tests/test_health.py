def test_health(anonymous_client):
    response = anonymous_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
