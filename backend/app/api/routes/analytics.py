from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder
from app.models.sale import Sale
from app.schemas.analytics import DashboardSummary
from app.services.inventory import inventory_rows

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(db: Session = Depends(get_db)):
    inventory = inventory_rows(db)
    latest_sale_at = db.scalar(select(func.max(Sale.sold_at)))
    weekly_revenue = 0.0
    category_sales: list[dict] = []
    if latest_sale_at is not None:
        week_cutoff = latest_sale_at - timedelta(days=6)
        weekly_revenue = float(
            db.scalar(
                select(func.coalesce(func.sum(Sale.quantity * Sale.unit_price), 0)).where(Sale.sold_at >= week_cutoff)
            )
            or 0
        )
        category_cutoff = latest_sale_at - timedelta(days=29)
        category_rows = db.execute(
            select(
                Product.category,
                func.coalesce(func.sum(Sale.quantity * Sale.unit_price), 0),
                func.coalesce(func.sum(Sale.quantity), 0),
            )
            .join(Product, Product.id == Sale.product_id)
            .where(Sale.sold_at >= category_cutoff)
            .group_by(Product.category)
            .order_by(Product.category)
        ).all()
        category_sales = [
            {"category": category, "revenue": float(revenue), "quantity": int(quantity)}
            for category, revenue, quantity in category_rows
        ]

    return {
        "weekly_revenue": round(weekly_revenue, 2),
        "low_stock_products": sum(row["stock_status"] in {"low", "critical"} for row in inventory),
        "critical_products": sum(row["stock_status"] == "critical" for row in inventory),
        "inventory_value": round(sum(row["inventory_cost"] for row in inventory), 2),
        "open_purchase_orders": int(
            db.scalar(select(func.count(PurchaseOrder.id)).where(PurchaseOrder.status.in_(["DRAFT", "APPROVED", "PARTIALLY_RECEIVED"]))) or 0
        ),
        "total_products": len(inventory),
        "category_sales_30_days": category_sales,
    }
