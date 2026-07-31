from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.services.inventory import create_inventory_transaction

router = APIRouter()


@router.get("", response_model=list[ProductOut])
def list_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    supplier_id: str | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    statement = select(Product)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern), Product.barcode.ilike(pattern)))
    if category:
        statement = statement.where(Product.category == category)
    if supplier_id:
        statement = statement.where(Product.supplier_id == supplier_id)
    if active_only:
        statement = statement.where(Product.is_active.is_(True))
    return db.scalars(statement.order_by(Product.category, Product.name)).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if not db.get(Supplier, payload.supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")
    values = payload.model_dump(exclude={"opening_stock"})
    product = Product(**values)
    db.add(product)
    try:
        db.flush()
        if payload.opening_stock:
            create_inventory_transaction(
                db,
                product_id=product.id,
                transaction_type="INITIAL_STOCK",
                quantity_change=payload.opening_stock,
                notes="Opening stock entered when product was created",
            )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product ID, SKU, or barcode already exists") from exc
    db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    changes = payload.model_dump(exclude_unset=True)
    if "supplier_id" in changes and not db.get(Supplier, changes["supplier_id"]):
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in changes.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product
