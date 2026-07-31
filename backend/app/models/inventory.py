from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow, uuid_str


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    product = relationship("Product", back_populates="inventory_transactions")
