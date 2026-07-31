from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SupplierCreate(BaseModel):
    id: str = Field(min_length=3, max_length=32)
    name: str = Field(min_length=2, max_length=160)
    email: str | None = None
    phone: str | None = None
    delivery_days: str | None = None
    minimum_order_amount: float = Field(default=0, ge=0)


class SupplierOut(ORMModel):
    id: str
    name: str
    email: str | None
    phone: str | None
    delivery_days: str | None
    minimum_order_amount: float
    created_at: datetime
    updated_at: datetime
