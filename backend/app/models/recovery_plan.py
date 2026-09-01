from pydantic import BaseModel, Field


class RecoveryPlan(BaseModel):
    plan_id: str
    action: str
    product_id: str | None = None
    offer_id: str | None = None

    customer_cost: float
    merchant_margin_percent: float

    constraint_safe: bool

    expected_revenue: float
    expected_margin_value: float

    success_probability: float = Field(
        default=0.0,
        ge=0,
        le=1,
    )

    expected_recovery_value: float = Field(
        default=0.0,
        ge=0,
    )

    explanation: str

    metadata: dict[str, str | int | float | bool] = {}