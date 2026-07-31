from sqlalchemy import func, select

from app.models import Product, Sale, Supplier, User


def test_admin_can_reset_demo_data(client, db_session, demo_user):
    response = client.post("/api/v1/demo/reset")
    assert response.status_code == 200
    body = response.json()
    assert body["products"] == 48
    assert body["suppliers"] == 4
    assert body["sales"] == 4067

    assert db_session.scalar(select(func.count(Product.id))) == 48
    assert db_session.scalar(select(func.count(Supplier.id))) == 4
    assert db_session.scalar(select(func.count(Sale.id))) == 4067
    assert db_session.get(User, demo_user.id) is not None
