from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierOut

router = APIRouter()


@router.get("", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    return db.scalars(select(Supplier).order_by(Supplier.name)).all()


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Supplier ID or name already exists") from exc
    db.refresh(supplier)
    return supplier
