from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryTransaction
from app.models.product import Product
from app.models.supplier import Supplier


def stock_status(current_stock: int, reorder_point: int) -> str:
    critical_threshold = max(2, round(reorder_point * 0.45))
    if current_stock <= critical_threshold:
        return "critical"
    if current_stock <= reorder_point:
        return "low"
    return "healthy"


def get_current_stock(db: Session, product_id: str) -> int:
    value = db.scalar(
        select(func.coalesce(func.sum(InventoryTransaction.quantity_change), 0)).where(
            InventoryTransaction.product_id == product_id
        )
    )
    return int(value or 0)


def inventory_rows(db: Session) -> list[dict]:
    stock_subquery = (
        select(
            InventoryTransaction.product_id.label("product_id"),
            func.coalesce(func.sum(InventoryTransaction.quantity_change), 0).label("current_stock"),
        )
        .group_by(InventoryTransaction.product_id)
        .subquery()
    )

    rows = db.execute(
        select(Product, Supplier, func.coalesce(stock_subquery.c.current_stock, 0))
        .join(Supplier, Supplier.id == Product.supplier_id)
        .outerjoin(stock_subquery, stock_subquery.c.product_id == Product.id)
        .order_by(Product.category, Product.name)
    ).all()

    result: list[dict] = []
    for product, supplier, current_stock in rows:
        current_stock = int(current_stock or 0)
        purchase_price = float(product.purchase_price)
        result.append(
            {
                "product_id": product.id,
                "sku": product.sku,
                "barcode": product.barcode,
                "product_name": product.name,
                "category": product.category,
                "supplier_id": supplier.id,
                "supplier_name": supplier.name,
                "current_stock": current_stock,
                "reorder_point": product.reorder_point,
                "safety_stock": product.safety_stock,
                "stock_status": stock_status(current_stock, product.reorder_point),
                "purchase_price": purchase_price,
                "inventory_cost": round(current_stock * purchase_price, 2),
            }
        )
    return result


def create_inventory_transaction(
    db: Session,
    *,
    product_id: str,
    transaction_type: str,
    quantity_change: int,
    reference_type: str | None = None,
    reference_id: str | None = None,
    notes: str | None = None,
) -> InventoryTransaction:
    transaction = InventoryTransaction(
        product_id=product_id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
    )
    db.add(transaction)
    db.flush()
    return transaction
