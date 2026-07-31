from pydantic import BaseModel


class CategorySales(BaseModel):
    category: str
    revenue: float
    quantity: int


class DashboardSummary(BaseModel):
    weekly_revenue: float
    low_stock_products: int
    critical_products: int
    inventory_value: float
    open_purchase_orders: int
    total_products: int
    category_sales_30_days: list[CategorySales]
