from pydantic import BaseModel


class RecoveryAction(BaseModel):
    action_id: str
    action_type: str

    product_id: str | None = None

    customer_cost: float
    merchant_value: float

    constraint_safe: bool

    reason: str