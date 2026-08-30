from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.services.replanning_service import ReplanningService


def test_failed_action_ids():

    service = ReplanningService()

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-001",
            action_id="SUB-P001",
            attempt_number=1,
            status="FAILED",
            reason="Payment failed.",
        )
    ]

    failed = service.get_failed_action_ids(attempts)

    assert failed == {"SUB-P001"}


def test_filter_failed_actions():

    service = ReplanningService()

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-001",
            action_id="SUB-P001",
            attempt_number=1,
            status="FAILED",
            reason="Payment failed.",
        )
    ]

    available = service.filter_failed_actions(
        ["SUB-P001", "SUB-P002"],
        attempts,
    )

    assert available == ["SUB-P002"]


def test_successful_attempt_is_not_removed():

    service = ReplanningService()

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-001",
            action_id="SUB-P001",
            attempt_number=1,
            status="SUCCESS",
            reason="Payment completed.",
        )
    ]

    available = service.filter_failed_actions(
        ["SUB-P001", "SUB-P002"],
        attempts,
    )

    assert available == ["SUB-P001", "SUB-P002"]


def test_next_attempt_number():

    service = ReplanningService()

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-001",
            action_id="SUB-P001",
            attempt_number=1,
            status="FAILED",
            reason="Payment failed.",
        ),
        RecoveryAttempt(
            attempt_id="ATT-002",
            transaction_id="TXN-001",
            action_id="SUB-P002",
            attempt_number=2,
            status="FAILED",
            reason="Payment failed.",
        ),
    ]

    assert service.next_attempt_number(attempts) == 3


def test_first_attempt_number():

    service = ReplanningService()

    assert service.next_attempt_number([]) == 1