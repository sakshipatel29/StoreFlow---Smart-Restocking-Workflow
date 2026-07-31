from datetime import datetime

from pydantic import BaseModel, Field


class PurchaseOrderCreateResult(BaseModel):
    created_order_ids: list[str]
    created_count: int


class PurchaseOrderItemOut(BaseModel):
    id: str
    product_id: str
    product_name: str
    sku: str
    quantity_cases: int
    quantity_units: int
    received_units: int
    unit_cost: float
    line_total: float


class PurchaseOrderOut(BaseModel):
    id: str
    po_number: str
    supplier_id: str
    supplier_name: str
    status: str
    estimated_total: float
    created_at: datetime
    approved_at: datetime | None
    received_at: datetime | None
    items: list[PurchaseOrderItemOut]


class ReceiveItem(BaseModel):
    product_id: str
    received_units: int = Field(gt=0)


class PurchaseOrderReceive(BaseModel):
    items: list[ReceiveItem] | None = None
