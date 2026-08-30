from pydantic import BaseModel


class ExecutionRequest(BaseModel):
    action_id: str

    customer_approved: bool = False

    policy_approved: bool = False