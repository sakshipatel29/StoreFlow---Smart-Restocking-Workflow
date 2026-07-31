import csv
import io
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.recommendation import ReorderRecommendation
from app.models.supplier import Supplier
from app.services.inventory import create_inventory_transaction


def next_po_number(db: Session) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    count = db.scalar(select(func.count(PurchaseOrder.id))) or 0
    return f"PO-{today}-{int(count) + 1:04d}"


def create_orders_from_recommendations(db: Session) -> list[PurchaseOrder]:
    rows = db.execute(
        select(ReorderRecommendation, Product)
        .join(Product, Product.id == ReorderRecommendation.product_id)
        .where(ReorderRecommendation.status.in_(["ACCEPTED", "MODIFIED"]))
        .where(~ReorderRecommendation.id.in_(select(PurchaseOrderItem.recommendation_id).where(PurchaseOrderItem.recommendation_id.is_not(None))))
        .order_by(Product.supplier_id, Product.name)
    ).all()

    grouped: dict[str, list[tuple[ReorderRecommendation, Product]]] = defaultdict(list)
    for recommendation, product in rows:
        grouped[product.supplier_id].append((recommendation, product))

    created: list[PurchaseOrder] = []
    for supplier_id, items in grouped.items():
        po = PurchaseOrder(
            po_number=next_po_number(db),
            supplier_id=supplier_id,
            status="DRAFT",
            estimated_total=Decimal("0.00"),
        )
        db.add(po)
        db.flush()

        estimated_total = Decimal("0.00")
        for recommendation, product in items:
            cases = recommendation.decided_cases if recommendation.status == "MODIFIED" else recommendation.recommended_cases
            cases = int(cases or 0)
            if cases <= 0:
                recommendation.status = "REJECTED"
                continue
            units = cases * product.units_per_case
            item = PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=product.id,
                recommendation_id=recommendation.id,
                quantity_cases=cases,
                quantity_units=units,
                unit_cost=product.purchase_price,
            )
            db.add(item)
            estimated_total += Decimal(units) * Decimal(str(product.purchase_price))
            recommendation.status = "ORDERED"

        po.estimated_total = estimated_total
        created.append(po)

    db.commit()
    return created


def get_order(db: Session, order_id: str) -> PurchaseOrder | None:
    return db.scalar(
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.product),
        )
        .where(PurchaseOrder.id == order_id)
    )


def order_to_dict(order: PurchaseOrder) -> dict:
    return {
        "id": order.id,
        "po_number": order.po_number,
        "supplier_id": order.supplier_id,
        "supplier_name": order.supplier.name,
        "status": order.status,
        "estimated_total": float(order.estimated_total),
        "created_at": order.created_at,
        "approved_at": order.approved_at,
        "received_at": order.received_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "sku": item.product.sku,
                "quantity_cases": item.quantity_cases,
                "quantity_units": item.quantity_units,
                "received_units": item.received_units,
                "unit_cost": float(item.unit_cost),
                "line_total": round(item.quantity_units * float(item.unit_cost), 2),
            }
            for item in order.items
        ],
    }


def receive_order(db: Session, order: PurchaseOrder, received_by_product: dict[str, int] | None) -> PurchaseOrder:
    if order.status == "RECEIVED":
        raise ValueError("Purchase order has already been received")
    if order.status not in {"DRAFT", "APPROVED"}:
        raise ValueError(f"Purchase order cannot be received from status {order.status}")

    for item in order.items:
        units = received_by_product.get(item.product_id, item.quantity_units) if received_by_product is not None else item.quantity_units
        if units <= 0:
            continue
        remaining = item.quantity_units - item.received_units
        if units > remaining:
            raise ValueError(f"Received units for {item.product.name} exceed the remaining ordered quantity")
        item.received_units += units
        create_inventory_transaction(
            db,
            product_id=item.product_id,
            transaction_type="PURCHASE_RECEIVED",
            quantity_change=units,
            reference_type="PURCHASE_ORDER",
            reference_id=order.id,
            notes=f"Received against {order.po_number}",
        )

    fully_received = all(item.received_units >= item.quantity_units for item in order.items)
    order.status = "RECEIVED" if fully_received else "PARTIALLY_RECEIVED"
    if fully_received:
        order.received_at = datetime.now(timezone.utc)
    db.commit()
    return get_order(db, order.id)


def order_csv(order: PurchaseOrder) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["po_number", "supplier", "status", "product_id", "sku", "product", "cases", "units", "unit_cost", "line_total"])
    for item in order.items:
        writer.writerow([
            order.po_number,
            order.supplier.name,
            order.status,
            item.product_id,
            item.product.sku,
            item.product.name,
            item.quantity_cases,
            item.quantity_units,
            f"{float(item.unit_cost):.2f}",
            f"{item.quantity_units * float(item.unit_cost):.2f}",
        ])
    return buffer.getvalue()
