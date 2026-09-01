from pydantic import BaseModel, Field

from backend.app.models.recovery_request import RecoveryRequest


class BatchRecoveryRequest(BaseModel):
    transactions: list[RecoveryRequest] = Field(
        min_length=1
    )

    simulation_mode: bool = False


class BatchRecoveryMetrics(BaseModel):
    transactions_evaluated: int
    recovery_eligible: int

    transactions_recovered: int
    transactions_failed: int
    transactions_blocked: int
    transactions_replanned: int
    transactions_escalated: int
    transactions_stopped: int

    revenue_at_risk: float
    revenue_recovered: float

    recovery_rate: float = Field(
        ge=0,
        le=1,
    )

    revenue_recovery_rate: float = Field(
        ge=0,
        le=1,
    )


class BatchRecoveryResponse(BaseModel):
    metrics: BatchRecoveryMetrics
    results: list[dict]
