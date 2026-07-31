from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_admin
from app.db.session import get_db
from app.models.user import User
from app.scripts.seed import reset_store_data, seed_store_data

router = APIRouter()


@router.post("/reset")
def reset_demo(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    reset_store_data(db)
    counts = seed_store_data(db)
    return {
        "status": "reset",
        "message": "StoreFlow demo data was restored to its original state.",
        **counts,
    }
