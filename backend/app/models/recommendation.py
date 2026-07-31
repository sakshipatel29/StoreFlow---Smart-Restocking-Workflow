from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow, uuid_str


class ReorderRecommendation(Base):
    __tablename__ = "reorder_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    generation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    current_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    average_daily_sales: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    coverage_days: Mapped[int] = mapped_column(Integer, nullable=False)
    units_on_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommended_units: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_cases: Mapped[int] = mapped_column(Integer, nullable=False)
    decided_cases: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING", index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    product = relationship("Product", back_populates="recommendations")
    purchase_order_item = relationship("PurchaseOrderItem", back_populates="recommendation", uselist=False)
