from datetime import datetime

from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    barcode: str
    quantity: int = Field(gt=0)
    unit_price: float | None = Field(default=None, gt=0)
    sold_at: datetime | None = None


class SaleOut(BaseModel):
    id: str
    product_id: str
    product_name: str
    barcode: str
    sold_at: datetime
    quantity: int
    unit_price: float
    revenue: float
    source: str


class ImportErrorRow(BaseModel):
    row_number: int
    reason: str
    raw: dict[str, str]


class SaleImportResult(BaseModel):
    import_id: str
    filename: str
    status: str
    rows_received: int
    rows_imported: int
    rows_rejected: int
    duplicates_skipped: int
    errors: list[ImportErrorRow]
