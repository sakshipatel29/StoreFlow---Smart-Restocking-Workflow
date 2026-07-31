import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale, SaleImport
from app.services.inventory import create_inventory_transaction

REQUIRED_COLUMNS = {"sold_at", "barcode", "quantity", "unit_price"}


def normalize_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def row_key(sold_at: datetime, barcode: str, quantity: int, unit_price: Decimal) -> str:
    normalized = f"{sold_at.isoformat()}|{barcode}|{quantity}|{unit_price.quantize(Decimal('0.01'))}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def import_sales_csv(db: Session, *, filename: str, content: bytes) -> dict:
    file_hash = hashlib.sha256(content).hexdigest()
    existing_import = db.scalar(select(SaleImport).where(SaleImport.file_hash == file_hash))
    if existing_import:
        return {
            "import_id": existing_import.id,
            "filename": existing_import.filename,
            "status": "DUPLICATE_FILE",
            "rows_received": existing_import.rows_received,
            "rows_imported": 0,
            "rows_rejected": 0,
            "duplicates_skipped": existing_import.rows_received,
            "errors": [],
        }

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(text))
    columns = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    products = {product.barcode: product for product in db.scalars(select(Product)).all()}
    existing_keys = set(db.scalars(select(Sale.external_key)).all())
    seen_keys: set[str] = set()
    prepared_rows: list[tuple[Product, datetime, int, Decimal, str]] = []
    errors: list[dict] = []
    duplicates = 0
    rows_received = 0

    for row_number, raw in enumerate(reader, start=2):
        rows_received += 1
        try:
            barcode = str(raw.get("barcode", "")).strip()
            product = products.get(barcode)
            if not product:
                raise ValueError(f"Unknown barcode: {barcode or '<blank>'}")

            sold_at = normalize_datetime(str(raw.get("sold_at", "")).strip())
            quantity = int(str(raw.get("quantity", "")).strip())
            if quantity <= 0:
                raise ValueError("quantity must be greater than zero")

            unit_price = Decimal(str(raw.get("unit_price", "")).strip())
            if unit_price <= 0:
                raise ValueError("unit_price must be greater than zero")

            external_key = row_key(sold_at, barcode, quantity, unit_price)
            if external_key in existing_keys or external_key in seen_keys:
                duplicates += 1
                continue

            seen_keys.add(external_key)
            prepared_rows.append((product, sold_at, quantity, unit_price, external_key))
        except (ValueError, InvalidOperation) as exc:
            errors.append({"row_number": row_number, "reason": str(exc), "raw": {k: str(v) for k, v in raw.items()}})

    sale_import = SaleImport(
        filename=filename,
        file_hash=file_hash,
        rows_received=rows_received,
        rows_imported=len(prepared_rows),
        rows_rejected=len(errors),
        duplicates_skipped=duplicates,
        status="COMPLETED_WITH_ERRORS" if errors else "COMPLETED",
        error_summary=json.dumps(errors[:50]) if errors else None,
    )
    db.add(sale_import)
    db.flush()

    for product, sold_at, quantity, unit_price, external_key in prepared_rows:
        sale = Sale(
            import_id=sale_import.id,
            product_id=product.id,
            sold_at=sold_at,
            quantity=quantity,
            unit_price=unit_price,
            external_key=external_key,
            source="CSV",
        )
        db.add(sale)
        db.flush()
        create_inventory_transaction(
            db,
            product_id=product.id,
            transaction_type="SALE",
            quantity_change=-quantity,
            reference_type="SALE",
            reference_id=sale.id,
            notes=f"Imported from {filename}",
        )

    db.commit()
    return {
        "import_id": sale_import.id,
        "filename": filename,
        "status": sale_import.status,
        "rows_received": rows_received,
        "rows_imported": len(prepared_rows),
        "rows_rejected": len(errors),
        "duplicates_skipped": duplicates,
        "errors": errors[:50],
    }
