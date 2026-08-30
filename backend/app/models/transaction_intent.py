from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TransactionIntent(BaseModel):
    category: str
    max_budget: Optional[float] = Field(default=None, gt=0)
    min_rating: Optional[float] = Field(default=None, ge=0, le=5)
    delivery_deadline_days: Optional[int] = Field(default=None, ge=0)

    quantity: int = Field(default=1, gt=0)

    hard_constraints: list[str] = []
    soft_preferences: list[str] = []

    @field_validator("category")
    @classmethod
    def category_must_not_be_empty(cls, value):
        if not value.strip():
            raise ValueError("Category cannot be empty")

        return value.strip().lower()