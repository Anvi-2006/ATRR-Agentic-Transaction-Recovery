from pydantic import BaseModel, Field


class RecoveryOutcome(BaseModel):
    intervention_id: str

    success_probability: float = Field(
        ge=0,
        le=1,
    )

    confidence: float = Field(
        ge=0,
        le=1,
    )

    factors: dict[str, float]

    explanation: str
