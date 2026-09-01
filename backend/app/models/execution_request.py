from typing import Literal

from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    action_id: str

    customer_approved: bool = False

    policy_approved: bool = False

    simulation_mode: bool = False

    attempt_number: int = 1

    simulation_scenario: Literal[
        "NORMAL",
        "REPLAN",
        "ESCALATE",
        "STOP",
    ] = "NORMAL"
