from pydantic import BaseModel, Field


class RevenueRisk(BaseModel):
    transaction_id: str
    risk_level: str
    risk_score: float = Field(ge=0, le=1)

    revenue_at_risk: float = Field(ge=0)
    recoverable_revenue: float = Field(ge=0)

    reason: str

    recovery_eligible: bool = True