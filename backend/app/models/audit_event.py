from datetime import datetime

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: str
    transaction_id: str
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_id: str | None = None
    status: str | None = None
    reason: str | None = None
    metadata: dict = Field(default_factory=dict)