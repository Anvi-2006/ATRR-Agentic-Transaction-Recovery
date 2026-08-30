from pydantic import BaseModel


class RecoveryAttempt(BaseModel):
    attempt_id: str
    transaction_id: str
    action_id: str
    attempt_number: int
    status: str
    reason: str