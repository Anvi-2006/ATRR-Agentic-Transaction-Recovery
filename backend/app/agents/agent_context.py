from typing import Literal

from pydantic import BaseModel

from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.recovery_attempt import RecoveryAttempt


class AgentContext(BaseModel):
    transaction_id: str

    intent: TransactionIntent

    recovery_plans: list[RecoveryPlan]

    merchant_policy: MerchantPolicy

    previous_attempts: list[RecoveryAttempt] = []

    simulation_scenario: Literal[
        "NORMAL",
        "REPLAN",
        "ESCALATE",
        "STOP",
    ] = "NORMAL"
