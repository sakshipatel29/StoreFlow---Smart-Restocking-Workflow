from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.inventory import InventoryTransaction
from app.models.product import Product
from app.schemas.inventory import InventoryAdjustment, InventoryItem, InventoryReceive, InventoryTransactionOut
from app.services.inventory import create_inventory_transaction, inventory_rows

router = APIRouter()


@router.get("", response_model=list[InventoryItem])
def list_inventory(stock_status: str | None = Query(default=None), db: Session = Depends(get_db)):
    rows = inventory_rows(db)
    if stock_status:
        rows = [row for row in rows if row["stock_status"] == stock_status.lower()]
    return rows


@router.get("/{product_id}/history", response_model=list[InventoryTransactionOut])
def inventory_history(product_id: str, db: Session = Depends(get_db)):
    if not db.get(Product, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return db.scalars(
        select(InventoryTransaction)
        .where(InventoryTransaction.product_id == product_id)
        .order_by(InventoryTransaction.created_at.desc())
    ).all()


@router.post("/receive", response_model=InventoryTransactionOut, status_code=status.HTTP_201_CREATED)
def receive_inventory(payload: InventoryReceive, db: Session = Depends(get_db)):
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    transaction = create_inventory_transaction(
        db,
        product_id=payload.product_id,
        transaction_type="PURCHASE_RECEIVED",
        quantity_change=payload.quantity,
        reference_type="MANUAL_RECEIVING",
        reference_id=payload.reference_id,
        notes=payload.notes,
    )
    db.commit()
    db.refresh(transaction)
    return transaction


@router.post("/adjust", response_model=InventoryTransactionOut, status_code=status.HTTP_201_CREATED)
def adjust_inventory(payload: InventoryAdjustment, db: Session = Depends(get_db)):
    if not db.get(Product, payload.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    transaction = create_inventory_transaction(
        db,
        product_id=payload.product_id,
        transaction_type=payload.transaction_type,
        quantity_change=payload.quantity_change,
        reference_type="MANUAL_ADJUSTMENT",
        notes=payload.notes,
    )
    db.commit()
    db.refresh(transaction)
    return transaction
