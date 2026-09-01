from typing import Literal

from pydantic import BaseModel, Field


class RecoveryRequest(BaseModel):
    transaction_id: str = Field(min_length=1)
    failed_product_id: str = Field(min_length=1)

    category: str = Field(min_length=1)

    max_budget: float | None = None
    min_rating: float | None = None
    delivery_deadline_days: int | None = None

    customer_approved: bool = True

    simulation_scenario: Literal[
        "NORMAL",
        "REPLAN",
        "ESCALATE",
        "STOP",
    ] = "NORMAL"
