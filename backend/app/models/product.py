from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    barcode: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    units_per_case: Mapped[int] = mapped_column(Integer, nullable=False)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    supplier = relationship("Supplier", back_populates="products")
    inventory_transactions = relationship("InventoryTransaction", back_populates="product")
    sales = relationship("Sale", back_populates="product")
    recommendations = relationship("ReorderRecommendation", back_populates="product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product")
