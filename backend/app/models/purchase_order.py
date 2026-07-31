from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow, uuid_str


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    po_number: Mapped[str] = mapped_column(String(40), unique=True, nullable=False, index=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="DRAFT", index=True)
    estimated_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    supplier = relationship("Supplier", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"
    __table_args__ = (UniqueConstraint("recommendation_id", name="uq_po_items_recommendation_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    purchase_order_id: Mapped[str] = mapped_column(ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    recommendation_id: Mapped[str | None] = mapped_column(ForeignKey("reorder_recommendations.id", ondelete="SET NULL"), nullable=True)
    quantity_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_units: Mapped[int] = mapped_column(Integer, nullable=False)
    received_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")
    recommendation = relationship("ReorderRecommendation", back_populates="purchase_order_item")
