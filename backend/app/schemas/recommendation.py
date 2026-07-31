from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class RecommendationGenerateRequest(BaseModel):
    history_days: int = Field(default=28, ge=7, le=365)
    review_cycle_days: int = Field(default=7, ge=1, le=30)


class RecommendationDecision(BaseModel):
    status: str
    decided_cases: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_decision(self):
        allowed = {"ACCEPTED", "MODIFIED", "REJECTED"}
        if self.status not in allowed:
            raise ValueError(f"status must be one of {sorted(allowed)}")
        if self.status == "MODIFIED" and self.decided_cases is None:
            raise ValueError("decided_cases is required when status is MODIFIED")
        return self


class RecommendationOut(BaseModel):
    id: str
    generation_id: str
    product_id: str
    product_name: str
    supplier_id: str
    supplier_name: str
    current_stock: int
    average_daily_sales: float
    coverage_days: int
    units_on_order: int
    recommended_units: int
    recommended_cases: int
    decided_cases: int | None
    reason: str
    status: str
    generated_at: datetime


class RecommendationGenerationResult(BaseModel):
    generation_id: str
    generated_count: int
    history_days: int
    review_cycle_days: int
    recommendations: list[RecommendationOut]
