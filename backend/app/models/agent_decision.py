from pydantic import BaseModel


class AgentDecision(BaseModel):
    selected_plan_id: str | None

    decision: str

    confidence: float

    reason: str

    replanning_required: bool