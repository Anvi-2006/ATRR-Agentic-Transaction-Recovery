from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.services.recovery_outcome_service import RecoveryOutcomeService


def create_action(action_type="payment_retry"):
    return RecoveryAction(
        action_id=f"TEST-{action_type}",
        action_type=action_type,
        product_id="P003",
        customer_cost=0,
        merchant_value=800,
        constraint_safe=True,
        success_probability=0.0,
        expected_recovery_value=0.0,
        reason="Test recovery action.",
    )


def test_outcome_probability_is_bounded():

    service = RecoveryOutcomeService()

    outcome = service.estimate(
        action=create_action()
    )

    assert 0 <= outcome.success_probability <= 1
    assert 0 <= outcome.confidence <= 1


def test_constraint_safe_action_gets_positive_constraint_factor():

    service = RecoveryOutcomeService()

    outcome = service.estimate(
        action=create_action("substitute_product")
    )

    assert outcome.factors["constraint_fit"] > 0
    assert outcome.success_probability > 0


def test_failed_previous_attempt_reduces_same_action_probability():

    service = RecoveryOutcomeService()

    action = create_action("payment_retry")

    baseline = service.estimate(action)

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-001",
            action_id=action.action_id,
            attempt_number=1,
            status="FAILED",
            reason="Payment retry failed.",
        )
    ]

    updated = service.estimate(
        action=action,
        previous_attempts=attempts,
    )

    assert updated.success_probability < baseline.success_probability
    assert updated.factors["previous_failure"] < 0


def test_first_payment_retry_gets_retry_factor():

    service = RecoveryOutcomeService()

    outcome = service.estimate(
        action=create_action("payment_retry")
    )

    assert outcome.factors["first_retry"] > 0


def test_outcome_contains_explanation():

    service = RecoveryOutcomeService()

    outcome = service.estimate(
        action=create_action("offer_incentive")
    )

    assert outcome.explanation
