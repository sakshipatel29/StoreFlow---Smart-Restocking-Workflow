from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.product import Product
from app.models.recommendation import ReorderRecommendation
from app.models.supplier import Supplier
from app.schemas.recommendation import (
    RecommendationDecision,
    RecommendationGenerateRequest,
    RecommendationGenerationResult,
    RecommendationOut,
)
from app.services.recommendations import generate_recommendations, recommendation_to_dict

router = APIRouter()


@router.post("/generate", response_model=RecommendationGenerationResult)
def generate(payload: RecommendationGenerateRequest, db: Session = Depends(get_db)):
    try:
        generation_id, recommendations = generate_recommendations(
            db,
            history_days=payload.history_days,
            review_cycle_days=payload.review_cycle_days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "generation_id": generation_id,
        "generated_count": len(recommendations),
        "history_days": payload.history_days,
        "review_cycle_days": payload.review_cycle_days,
        "recommendations": recommendations,
    }


@router.get("", response_model=list[RecommendationOut])
def list_recommendations(generation_id: str | None = None, db: Session = Depends(get_db)):
    if generation_id is None:
        generation_id = db.scalar(
            select(ReorderRecommendation.generation_id)
            .order_by(ReorderRecommendation.generated_at.desc())
            .limit(1)
        )
    if generation_id is None:
        return []
    rows = db.execute(
        select(ReorderRecommendation, Product, Supplier)
        .join(Product, Product.id == ReorderRecommendation.product_id)
        .join(Supplier, Supplier.id == Product.supplier_id)
        .where(ReorderRecommendation.generation_id == generation_id)
        .order_by(Supplier.name, Product.name)
    ).all()
    return [recommendation_to_dict(rec, product, supplier) for rec, product, supplier in rows]


@router.patch("/{recommendation_id}", response_model=RecommendationOut)
def decide_recommendation(recommendation_id: str, payload: RecommendationDecision, db: Session = Depends(get_db)):
    row = db.execute(
        select(ReorderRecommendation, Product, Supplier)
        .join(Product, Product.id == ReorderRecommendation.product_id)
        .join(Supplier, Supplier.id == Product.supplier_id)
        .where(ReorderRecommendation.id == recommendation_id)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    recommendation, product, supplier = row
    if recommendation.status not in {"PENDING", "ACCEPTED", "MODIFIED", "REJECTED"}:
        raise HTTPException(status_code=409, detail=f"Recommendation cannot be changed from status {recommendation.status}")
    recommendation.status = payload.status
    recommendation.decided_cases = payload.decided_cases if payload.status == "MODIFIED" else None
    db.commit()
    db.refresh(recommendation)
    return recommendation_to_dict(recommendation, product, supplier)
