from pydantic import BaseModel, Field


class RecoveryIntervention(BaseModel):
    intervention_id: str
    intervention_type: str

    product_id: str | None = None
    offer_id: str | None = None

    revenue_at_risk: float = Field(default=0.0, ge=0)
    recoverable_revenue: float = Field(default=0.0, ge=0)

    customer_cost: float = Field(default=0.0, ge=0)
    merchant_cost: float = Field(default=0.0, ge=0)

    success_probability: float = Field(
        default=0.0,
        ge=0,
        le=1,
    )

    expected_recovery_value: float = Field(
        default=0.0,
        ge=0,
    )

    constraint_safe: bool = False
    policy_safe: bool = False

    reason: str

    metadata: dict[str, str | int | float | bool] = {}
