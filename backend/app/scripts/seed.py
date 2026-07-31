import argparse
import csv
import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password, verify_password
from app.db.session import SessionLocal
from app.models import (
    InventoryTransaction,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    ReorderRecommendation,
    Sale,
    SaleImport,
    Supplier,
    User,
)
from app.services.sales import normalize_datetime, row_key

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def ensure_demo_user(db: Session) -> User:
    email = settings.demo_admin_email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user:
        # Keep the deployed demo account synchronized with Render settings.
        if not verify_password(
            settings.demo_admin_password,
            user.password_hash,
        ):
            user.password_hash = hash_password(
                settings.demo_admin_password
            )

        user.full_name = settings.demo_admin_name
        user.role = "admin"
        user.is_active = True

        db.flush()
        return user

    user = User(
        email=email,
        full_name=settings.demo_admin_name,
        password_hash=hash_password(
            settings.demo_admin_password
        ),
        role="admin",
        is_active=True,
    )

    db.add(user)
    db.flush()
    return user


def reset_store_data(db: Session) -> None:
    # Users are deliberately preserved so an administrator can reset the public demo safely.
    for model in [
        PurchaseOrderItem,
        PurchaseOrder,
        ReorderRecommendation,
        InventoryTransaction,
        Sale,
        SaleImport,
        Product,
        Supplier,
    ]:
        db.execute(delete(model))
    db.commit()


def seed_store_data(db: Session) -> dict[str, int]:
    suppliers = read_csv("suppliers.csv")
    products = read_csv("products.csv")
    sales = read_csv("sales_90_days.csv")
    adjustments = read_csv("inventory_adjustments.csv")

    for row in suppliers:
        db.add(
            Supplier(
                id=row["id"],
                name=row["name"],
                email=row["email"] or None,
                phone=row["phone"] or None,
                delivery_days=row["delivery_days"] or None,
                minimum_order_amount=Decimal(row["minimum_order_amount"]),
            )
        )
    db.flush()

    adjustment_totals: dict[str, int] = defaultdict(int)
    for row in adjustments:
        adjustment_totals[row["barcode"]] += int(row["quantity_change"])

    barcode_to_product: dict[str, Product] = {}
    for row in products:
        product = Product(
            id=row["id"],
            sku=row["sku"],
            barcode=row["barcode"],
            name=row["name"],
            category=row["category"],
            supplier_id=row["supplier_id"],
            purchase_price=Decimal(row["purchase_price"]),
            selling_price=Decimal(row["selling_price"]),
            units_per_case=int(row["units_per_case"]),
            reorder_point=int(row["reorder_point"]),
            safety_stock=int(row["safety_stock"]),
            lead_time_days=int(row["lead_time_days"]),
            is_active=True,
        )
        db.add(product)
        barcode_to_product[product.barcode] = product
    db.flush()

    for row in products:
        final_stock = int(row["current_stock"])
        opening_stock = final_stock - adjustment_totals.get(row["barcode"], 0)
        db.add(
            InventoryTransaction(
                product_id=row["id"],
                transaction_type="INITIAL_STOCK",
                quantity_change=opening_stock,
                notes="Opening quantity loaded from the StoreFlow demo dataset",
                created_at=datetime(2026, 5, 2, 23, 59, tzinfo=timezone.utc),
            )
        )

    for row in adjustments:
        product = barcode_to_product[row["barcode"]]
        db.add(
            InventoryTransaction(
                product_id=product.id,
                transaction_type=row["transaction_type"],
                quantity_change=int(row["quantity_change"]),
                notes=row["notes"],
                created_at=normalize_datetime(row["created_at"]),
            )
        )

    sales_content = (DATA_DIR / "sales_90_days.csv").read_bytes()
    import_record = SaleImport(
        filename="sales_90_days.csv",
        file_hash=hashlib.sha256(sales_content).hexdigest(),
        rows_received=len(sales),
        rows_imported=len(sales),
        rows_rejected=0,
        duplicates_skipped=0,
        status="SEEDED_HISTORY",
    )
    db.add(import_record)
    db.flush()

    for row in sales:
        product = barcode_to_product[row["barcode"]]
        sold_at = normalize_datetime(row["sold_at"])
        quantity = int(row["quantity"])
        unit_price = Decimal(row["unit_price"])
        db.add(
            Sale(
                import_id=import_record.id,
                product_id=product.id,
                sold_at=sold_at,
                quantity=quantity,
                unit_price=unit_price,
                external_key=row_key(sold_at, product.barcode, quantity, unit_price),
                source="SEED_HISTORY",
            )
        )

    db.commit()
    return {
        "suppliers": len(suppliers),
        "products": len(products),
        "sales": len(sales),
        "adjustments": len(adjustments),
    }


def seed(reset: bool = False) -> None:
    db = SessionLocal()
    try:
        if reset:
            reset_store_data(db)
        user = ensure_demo_user(db)
        if db.scalar(select(Product.id).limit(1)):
            db.commit()
            print(
                "Seed skipped: products already exist. "
                f"Demo login is {user.email}. Use --reset to reload store data."
            )
            return
        counts = seed_store_data(db)
        print(
            f"Seeded {counts['suppliers']} suppliers, {counts['products']} products, "
            f"{counts['sales']} sales, {counts['adjustments']} adjustments, and demo administrator {user.email}."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed StoreFlow demo data")
    parser.add_argument("--reset", action="store_true", help="Delete existing store data before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
