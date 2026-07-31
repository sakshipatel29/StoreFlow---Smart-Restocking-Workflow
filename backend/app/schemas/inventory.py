from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class InventoryItem(BaseModel):
    product_id: str
    sku: str
    barcode: str
    product_name: str
    category: str
    supplier_id: str
    supplier_name: str
    current_stock: int
    reorder_point: int
    safety_stock: int
    stock_status: str
    purchase_price: float
    inventory_cost: float


class InventoryReceive(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    reference_id: str | None = None
    notes: str | None = None


class InventoryAdjustment(BaseModel):
    product_id: str
    transaction_type: str
    quantity_change: int
    notes: str | None = None

    @model_validator(mode="after")
    def validate_change(self):
        if self.quantity_change == 0:
            raise ValueError("quantity_change cannot be zero")
        allowed = {"DAMAGE", "EXPIRATION", "RETURN", "MANUAL_ADJUSTMENT", "THEFT"}
        if self.transaction_type not in allowed:
            raise ValueError(f"transaction_type must be one of {sorted(allowed)}")
        return self


class InventoryTransactionOut(ORMModel):
    id: str
    product_id: str
    transaction_type: str
    quantity_change: int
    reference_type: str | None
    reference_id: str | None
    notes: str | None
    created_at: datetime
