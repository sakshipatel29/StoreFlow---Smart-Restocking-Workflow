"""Initial StoreFlow schema

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260731_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "suppliers",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("delivery_days", sa.String(length=80), nullable=True),
        sa.Column("minimum_order_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_suppliers_name"), "suppliers", ["name"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("barcode", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("supplier_id", sa.String(length=32), nullable=False),
        sa.Column("purchase_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("units_per_case", sa.Integer(), nullable=False),
        sa.Column("reorder_point", sa.Integer(), nullable=False),
        sa.Column("safety_stock", sa.Integer(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("barcode"),
        sa.UniqueConstraint("sku"),
    )
    for column in ["barcode", "category", "is_active", "name", "sku", "supplier_id"]:
        op.create_index(op.f(f"ix_products_{column}"), "products", [column], unique=False)

    op.create_table(
        "sale_imports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("rows_received", sa.Integer(), nullable=False),
        sa.Column("rows_imported", sa.Integer(), nullable=False),
        sa.Column("rows_rejected", sa.Integer(), nullable=False),
        sa.Column("duplicates_skipped", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_hash"),
    )
    op.create_index(op.f("ix_sale_imports_created_at"), "sale_imports", ["created_at"], unique=False)
    op.create_index(op.f("ix_sale_imports_file_hash"), "sale_imports", ["file_hash"], unique=False)

    op.create_table(
        "inventory_transactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("transaction_type", sa.String(length=40), nullable=False),
        sa.Column("quantity_change", sa.Integer(), nullable=False),
        sa.Column("reference_type", sa.String(length=40), nullable=True),
        sa.Column("reference_id", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ["created_at", "product_id", "reference_id", "transaction_type"]:
        op.create_index(op.f(f"ix_inventory_transactions_{column}"), "inventory_transactions", [column], unique=False)

    op.create_table(
        "sales",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("import_id", sa.String(length=36), nullable=True),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("sold_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("external_key", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["import_id"], ["sale_imports.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_key", name="uq_sales_external_key"),
    )
    for column in ["external_key", "import_id", "product_id", "sold_at"]:
        op.create_index(op.f(f"ix_sales_{column}"), "sales", [column], unique=False)

    op.create_table(
        "reorder_recommendations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("generation_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("current_stock", sa.Integer(), nullable=False),
        sa.Column("average_daily_sales", sa.Numeric(12, 3), nullable=False),
        sa.Column("coverage_days", sa.Integer(), nullable=False),
        sa.Column("units_on_order", sa.Integer(), nullable=False),
        sa.Column("recommended_units", sa.Integer(), nullable=False),
        sa.Column("recommended_cases", sa.Integer(), nullable=False),
        sa.Column("decided_cases", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ["generated_at", "generation_id", "product_id", "status"]:
        op.create_index(op.f(f"ix_reorder_recommendations_{column}"), "reorder_recommendations", [column], unique=False)

    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("po_number", sa.String(length=40), nullable=False),
        sa.Column("supplier_id", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("estimated_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("po_number"),
    )
    for column in ["created_at", "po_number", "status", "supplier_id"]:
        op.create_index(op.f(f"ix_purchase_orders_{column}"), "purchase_orders", [column], unique=False)

    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("purchase_order_id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=32), nullable=False),
        sa.Column("recommendation_id", sa.String(length=36), nullable=True),
        sa.Column("quantity_cases", sa.Integer(), nullable=False),
        sa.Column("quantity_units", sa.Integer(), nullable=False),
        sa.Column("received_units", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recommendation_id"], ["reorder_recommendations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("recommendation_id", name="uq_po_items_recommendation_id"),
    )
    op.create_index(op.f("ix_purchase_order_items_product_id"), "purchase_order_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_purchase_order_items_purchase_order_id"), "purchase_order_items", ["purchase_order_id"], unique=False)


def downgrade() -> None:
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_orders")
    op.drop_table("reorder_recommendations")
    op.drop_table("sales")
    op.drop_table("inventory_transactions")
    op.drop_table("sale_imports")
    op.drop_table("products")
    op.drop_table("suppliers")
