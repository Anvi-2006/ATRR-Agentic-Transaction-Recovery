from pydantic import BaseModel


class ExecutionResult(BaseModel):
    executed: bool

    status: str

    reason: str

    action_id: str