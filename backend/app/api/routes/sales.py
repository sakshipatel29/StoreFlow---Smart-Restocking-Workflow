import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleImportResult, SaleOut
from app.services.inventory import create_inventory_transaction
from app.services.sales import import_sales_csv, row_key

router = APIRouter()


def sale_to_dict(sale: Sale, product: Product) -> dict:
    return {
        "id": sale.id,
        "product_id": product.id,
        "product_name": product.name,
        "barcode": product.barcode,
        "sold_at": sale.sold_at,
        "quantity": sale.quantity,
        "unit_price": float(sale.unit_price),
        "revenue": round(sale.quantity * float(sale.unit_price), 2),
        "source": sale.source,
    }


@router.get("", response_model=list[SaleOut])
def list_sales(limit: int = Query(default=100, ge=1, le=1000), db: Session = Depends(get_db)):
    rows = db.execute(
        select(Sale, Product)
        .join(Product, Product.id == Sale.product_id)
        .order_by(Sale.sold_at.desc())
        .limit(limit)
    ).all()
    return [sale_to_dict(sale, product) for sale, product in rows]


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    product = db.scalar(select(Product).where(Product.barcode == payload.barcode))
    if not product:
        raise HTTPException(status_code=404, detail="Unknown barcode")
    sold_at = payload.sold_at or datetime.now(timezone.utc)
    unit_price = Decimal(str(payload.unit_price if payload.unit_price is not None else product.selling_price))
    external_key = row_key(sold_at, product.barcode, payload.quantity, unit_price)
    if db.scalar(select(Sale).where(Sale.external_key == external_key)):
        raise HTTPException(status_code=409, detail="Duplicate sale")
    sale = Sale(
        product_id=product.id,
        sold_at=sold_at,
        quantity=payload.quantity,
        unit_price=unit_price,
        external_key=external_key,
        source="CHECKOUT",
    )
    db.add(sale)
    db.flush()
    create_inventory_transaction(
        db,
        product_id=product.id,
        transaction_type="SALE",
        quantity_change=-payload.quantity,
        reference_type="SALE",
        reference_id=sale.id,
        notes="Checkout sale",
    )
    db.commit()
    db.refresh(sale)
    return sale_to_dict(sale, product)


@router.post("/import", response_model=SaleImportResult)
async def upload_sales_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Upload a .csv file")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV file is larger than 10 MB")
    try:
        return import_sales_csv(db, filename=file.filename, content=content)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
