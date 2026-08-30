from backend.app.services.audit_service import AuditService


def test_record_audit_event():

    service = AuditService()

    event = service.record(
        transaction_id="TXN-001",
        event_type="TRANSACTION_FAILED",
        status="FAILED",
        reason="Payment attempt failed.",
    )

    assert event.event_id == "EVT-0001"
    assert event.transaction_id == "TXN-001"
    assert event.event_type == "TRANSACTION_FAILED"


def test_record_event_with_action():

    service = AuditService()

    event = service.record(
        transaction_id="TXN-001",
        event_type="POLICY_CHECKED",
        action_id="SUB-P001",
        status="APPROVED",
        reason="Action allowed by merchant policy.",
    )

    assert event.action_id == "SUB-P001"
    assert event.status == "APPROVED"


def test_get_transaction_events():

    service = AuditService()

    service.record(
        transaction_id="TXN-001",
        event_type="TRANSACTION_FAILED",
    )

    service.record(
        transaction_id="TXN-002",
        event_type="TRANSACTION_FAILED",
    )

    events = service.get_transaction_events("TXN-001")

    assert len(events) == 1
    assert events[0].transaction_id == "TXN-001"


def test_events_are_returned_in_order():

    service = AuditService()

    service.record(
        transaction_id="TXN-001",
        event_type="TRANSACTION_FAILED",
    )

    service.record(
        transaction_id="TXN-001",
        event_type="RECOVERY_STARTED",
    )

    events = service.get_transaction_events("TXN-001")

    assert events[0].event_type == "TRANSACTION_FAILED"
    assert events[1].event_type == "RECOVERY_STARTED"


def test_metadata_is_stored():

    service = AuditService()

    event = service.record(
        transaction_id="TXN-001",
        event_type="RECOVERY_PLAN_CREATED",
        metadata={
            "product_id": "P001",
            "expected_margin": 809.82,
        },
    )

    assert event.metadata["product_id"] == "P001"
    assert event.metadata["expected_margin"] == 809.82