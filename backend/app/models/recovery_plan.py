from pydantic import BaseModel


class RecoveryPlan(BaseModel):
    plan_id: str
    action: str
    product_id: str | None = None

    customer_cost: float
    merchant_margin_percent: float

    constraint_safe: bool

    expected_revenue: float
    expected_margin_value: float

    explanation: str