from pydantic import BaseModel


class MerchantPolicy(BaseModel):
    max_discount_percent: float
    max_incentive_amount: float

    allowed_actions: list[str]

    require_customer_confirmation: bool = True