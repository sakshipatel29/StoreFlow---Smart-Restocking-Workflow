from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProductCreate(BaseModel):
    id: str = Field(min_length=3, max_length=32)
    sku: str = Field(min_length=2, max_length=80)
    barcode: str = Field(min_length=4, max_length=80)
    name: str = Field(min_length=2, max_length=180)
    category: str = Field(min_length=2, max_length=80)
    supplier_id: str
    purchase_price: float = Field(gt=0)
    selling_price: float = Field(gt=0)
    units_per_case: int = Field(gt=0)
    reorder_point: int = Field(ge=0)
    safety_stock: int = Field(default=0, ge=0)
    lead_time_days: int = Field(default=1, ge=0)
    is_active: bool = True
    opening_stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    category: str | None = None
    supplier_id: str | None = None
    purchase_price: float | None = Field(default=None, gt=0)
    selling_price: float | None = Field(default=None, gt=0)
    units_per_case: int | None = Field(default=None, gt=0)
    reorder_point: int | None = Field(default=None, ge=0)
    safety_stock: int | None = Field(default=None, ge=0)
    lead_time_days: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(ORMModel):
    id: str
    sku: str
    barcode: str
    name: str
    category: str
    supplier_id: str
    purchase_price: float
    selling_price: float
    units_per_case: int
    reorder_point: int
    safety_stock: int
    lead_time_days: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
