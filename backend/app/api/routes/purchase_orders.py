from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.schemas.purchase_order import PurchaseOrderCreateResult, PurchaseOrderOut, PurchaseOrderReceive
from app.services.purchase_orders import (
    create_orders_from_recommendations,
    get_order,
    order_csv,
    order_to_dict,
    receive_order,
)

router = APIRouter()


@router.post("/from-recommendations", response_model=PurchaseOrderCreateResult, status_code=status.HTTP_201_CREATED)
def create_from_recommendations(db: Session = Depends(get_db)):
    orders = create_orders_from_recommendations(db)
    if not orders:
        raise HTTPException(status_code=400, detail="No accepted or modified recommendations are ready for ordering")
    return {"created_order_ids": [order.id for order in orders], "created_count": len(orders)}


@router.get("", response_model=list[PurchaseOrderOut])
def list_orders(db: Session = Depends(get_db)):
    orders = db.scalars(
        select(PurchaseOrder)
        .options(
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.items).selectinload(PurchaseOrderItem.product),
        )
        .order_by(PurchaseOrder.created_at.desc())
    ).all()
    return [order_to_dict(order) for order in orders]


@router.get("/{order_id}", response_model=PurchaseOrderOut)
def read_order(order_id: str, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return order_to_dict(order)


@router.post("/{order_id}/approve", response_model=PurchaseOrderOut)
def approve_order(order_id: str, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    if order.status != "DRAFT":
        raise HTTPException(status_code=409, detail="Only draft purchase orders can be approved")
    order.status = "APPROVED"
    order.approved_at = datetime.now(timezone.utc)
    db.commit()
    return order_to_dict(get_order(db, order.id))


@router.post("/{order_id}/receive", response_model=PurchaseOrderOut)
def receive_purchase_order(order_id: str, payload: PurchaseOrderReceive, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    received_by_product = None if payload.items is None else {item.product_id: item.received_units for item in payload.items}
    try:
        updated = receive_order(db, order, received_by_product)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return order_to_dict(updated)


@router.get("/{order_id}/export")
def export_purchase_order(order_id: str, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    content = order_csv(order)
    headers = {"Content-Disposition": f'attachment; filename="{order.po_number}.csv"'}
    return Response(content=content, media_type="text/csv", headers=headers)
