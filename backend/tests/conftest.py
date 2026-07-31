import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import InventoryTransaction, Product, Supplier, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def demo_user(db_session):
    user = User(
        email="owner@storeflow.example.com",
        full_name="Test Store Owner",
        password_hash=hash_password("StoreFlow123!"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_headers(demo_user):
    token = create_access_token(demo_user.id, demo_user.role, expires_minutes=10)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def anonymous_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def client(db_session, auth_headers):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, headers=auth_headers) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def seeded_store(db_session):
    supplier = Supplier(
        id="SUP-001",
        name="Test Supplier",
        email="supplier@example.com",
        delivery_days="Mon",
        minimum_order_amount=0,
    )
    product = Product(
        id="PRD-001",
        sku="TEST-001",
        barcode="111111111111",
        name="Test Soda",
        category="Beverages",
        supplier_id="SUP-001",
        purchase_price=1.00,
        selling_price=2.50,
        units_per_case=12,
        reorder_point=10,
        safety_stock=5,
        lead_time_days=3,
        is_active=True,
    )
    db_session.add_all([supplier, product])
    db_session.flush()
    db_session.add(
        InventoryTransaction(
            product_id=product.id,
            transaction_type="INITIAL_STOCK",
            quantity_change=4,
            notes="Test opening stock",
        )
    )
    db_session.commit()
    return {"supplier": supplier, "product": product}
