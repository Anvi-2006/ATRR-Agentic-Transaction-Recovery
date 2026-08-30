from backend.app.models.audit_event import AuditEvent


class AuditService:

    def __init__(self):
        self._events: list[AuditEvent] = []

    def record(
        self,
        transaction_id: str,
        event_type: str,
        action_id: str | None = None,
        status: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            event_id=f"EVT-{len(self._events) + 1:04d}",
            transaction_id=transaction_id,
            event_type=event_type,
            action_id=action_id,
            status=status,
            reason=reason,
            metadata=metadata or {},
        )

        self._events.append(event)

        return event

    def get_transaction_events(
        self,
        transaction_id: str,
    ) -> list[AuditEvent]:

        return [
            event
            for event in self._events
            if event.transaction_id == transaction_id
        ]

    def get_all_events(self) -> list[AuditEvent]:

        return list(self._events)