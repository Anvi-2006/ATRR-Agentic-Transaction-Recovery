from pydantic import BaseModel, Field


class AgentDecision(BaseModel):
    selected_plan_id: str | None = None

    decision: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reason: str

    replanning_required: bool = False

    escalation_required: bool = False

    stop_reason: str | None = None
