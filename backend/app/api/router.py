from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.api.routes import analytics, auth, demo, inventory, products, purchase_orders, recommendations, sales, suppliers

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo administration"])

protected_router = APIRouter(dependencies=[Depends(get_current_user)])
protected_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
protected_router.include_router(products.router, prefix="/products", tags=["products"])
protected_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
protected_router.include_router(sales.router, prefix="/sales", tags=["sales"])
protected_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
protected_router.include_router(purchase_orders.router, prefix="/purchase-orders", tags=["purchase-orders"])
protected_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(protected_router)
