from pydantic import BaseModel, Field


class MerchantPolicy(BaseModel):
    max_discount_percent: float = Field(default=10.0, ge=0)
    max_incentive_amount: float = Field(default=500.0, ge=0)

    min_margin_percent: float = Field(default=0.0, ge=0)

    allow_product_substitution: bool = True
    allow_payment_retry: bool = True
    max_payment_retries: int = Field(default=0, ge=0)

    allowed_actions: list[str] = []

    require_customer_confirmation: bool = True

    allow_escalation: bool = True
    max_automated_attempts: int = Field(default=3, ge=1)
    minimum_expected_recovery_value: float = Field(
        default=100.0,
        ge=0,
    )
