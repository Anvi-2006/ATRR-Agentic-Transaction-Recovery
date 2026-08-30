from pydantic import BaseModel


class PolicyDecision(BaseModel):
    allowed: bool

    reason: str

    policy_checks: dict[str, bool]