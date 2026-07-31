import math
from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.inventory import InventoryTransaction
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.recommendation import ReorderRecommendation
from app.models.sale import Sale
from app.models.supplier import Supplier


def _stock_map(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(
            InventoryTransaction.product_id,
            func.coalesce(func.sum(InventoryTransaction.quantity_change), 0),
        ).group_by(InventoryTransaction.product_id)
    ).all()
    return {product_id: int(quantity or 0) for product_id, quantity in rows}


def _on_order_map(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(PurchaseOrderItem.product_id, func.coalesce(func.sum(PurchaseOrderItem.quantity_units), 0))
        .join(PurchaseOrder, PurchaseOrder.id == PurchaseOrderItem.purchase_order_id)
        .where(PurchaseOrder.status.in_(["DRAFT", "APPROVED"]))
        .group_by(PurchaseOrderItem.product_id)
    ).all()
    return {product_id: int(quantity or 0) for product_id, quantity in rows}


def recommendation_to_dict(recommendation: ReorderRecommendation, product: Product, supplier: Supplier) -> dict:
    return {
        "id": recommendation.id,
        "generation_id": recommendation.generation_id,
        "product_id": product.id,
        "product_name": product.name,
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "current_stock": recommendation.current_stock,
        "average_daily_sales": float(recommendation.average_daily_sales),
        "coverage_days": recommendation.coverage_days,
        "units_on_order": recommendation.units_on_order,
        "recommended_units": recommendation.recommended_units,
        "recommended_cases": recommendation.recommended_cases,
        "decided_cases": recommendation.decided_cases,
        "reason": recommendation.reason,
        "status": recommendation.status,
        "generated_at": recommendation.generated_at,
    }


def generate_recommendations(db: Session, *, history_days: int, review_cycle_days: int) -> tuple[str, list[dict]]:
    latest_sale_at = db.scalar(select(func.max(Sale.sold_at)))
    if latest_sale_at is None:
        raise ValueError("No sales history is available. Import sales before generating recommendations.")

    cutoff = latest_sale_at - timedelta(days=history_days - 1)
    sales_rows = db.execute(
        select(Sale.product_id, func.coalesce(func.sum(Sale.quantity), 0))
        .where(Sale.sold_at >= cutoff, Sale.sold_at <= latest_sale_at)
        .group_by(Sale.product_id)
    ).all()
    sold_map = {product_id: int(quantity or 0) for product_id, quantity in sales_rows}
    stock_map = _stock_map(db)
    on_order_map = _on_order_map(db)

    db.execute(
        update(ReorderRecommendation)
        .where(ReorderRecommendation.status.in_(["PENDING", "ACCEPTED", "MODIFIED"]))
        .values(status="SUPERSEDED")
    )

    generation_id = str(uuid4())
    results: list[dict] = []
    rows = db.execute(
        select(Product, Supplier)
        .join(Supplier, Supplier.id == Product.supplier_id)
        .where(Product.is_active.is_(True))
        .order_by(Supplier.name, Product.name)
    ).all()

    for product, supplier in rows:
        average_daily_sales = Decimal(sold_map.get(product.id, 0)) / Decimal(history_days)
        current_stock = stock_map.get(product.id, 0)
        units_on_order = on_order_map.get(product.id, 0)
        coverage_days = product.lead_time_days + review_cycle_days
        target_stock = average_daily_sales * Decimal(coverage_days) + Decimal(product.safety_stock)
        required_units = max(Decimal(0), target_stock - Decimal(current_stock) - Decimal(units_on_order))
        recommended_cases = math.ceil(float(required_units) / product.units_per_case) if required_units > 0 else 0
        if recommended_cases <= 0:
            continue
        recommended_units = recommended_cases * product.units_per_case
        reason = (
            f"Current stock is {current_stock} units. Average sales are "
            f"{float(average_daily_sales):.1f} units/day over {history_days} days. "
            f"The target covers {coverage_days} days plus {product.safety_stock} safety-stock units. "
            f"{units_on_order} units are already on order."
        )
        recommendation = ReorderRecommendation(
            generation_id=generation_id,
            product_id=product.id,
            current_stock=current_stock,
            average_daily_sales=average_daily_sales,
            coverage_days=coverage_days,
            units_on_order=units_on_order,
            recommended_units=recommended_units,
            recommended_cases=recommended_cases,
            reason=reason,
            status="PENDING",
        )
        db.add(recommendation)
        db.flush()
        results.append(recommendation_to_dict(recommendation, product, supplier))

    db.commit()
    return generation_id, results
