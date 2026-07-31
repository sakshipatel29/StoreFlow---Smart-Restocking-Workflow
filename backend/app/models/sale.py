from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import utcnow, uuid_str


class SaleImport(Base):
    __tablename__ = "sale_imports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    rows_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_imported: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicates_skipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="COMPLETED")
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    sales = relationship("Sale", back_populates="sale_import")


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (UniqueConstraint("external_key", name="uq_sales_external_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    import_id: Mapped[str | None] = mapped_column(ForeignKey("sale_imports.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    sold_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    external_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="CSV")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    sale_import = relationship("SaleImport", back_populates="sales")
    product = relationship("Product", back_populates="sales")
