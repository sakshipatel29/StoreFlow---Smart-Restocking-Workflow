def test_business_routes_require_authentication(anonymous_client):
    response = anonymous_client.get("/api/v1/products")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_login_and_current_user(anonymous_client, demo_user):
    login = anonymous_client.post(
        "/api/v1/auth/login",
        json={"email": demo_user.email, "password": "StoreFlow123!"},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == demo_user.email

    me = anonymous_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["role"] == "admin"


def test_login_rejects_wrong_password(anonymous_client, demo_user):
    response = anonymous_client.post(
        "/api/v1/auth/login",
        json={"email": demo_user.email, "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
