from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.services.recovery_orchestrator import RecoveryOrchestrator


def build_intent():
    return TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
    )


def build_policy():
    return MerchantPolicy(
        max_discount_percent=10,
        max_incentive_amount=500,
        allowed_actions=[
            "substitute_product",
            "change_delivery",
            "offer_incentive",
        ],
    )


def test_successful_recovery():

    orchestrator = RecoveryOrchestrator()

    result = orchestrator.run(
        transaction_id="TXN-001",
        intent=build_intent(),
        failed_product_id="P003",
        merchant_policy=build_policy(),
        customer_approved=True,
    )

    assert result["status"] == "RECOVERED"
    assert result["selected_action"] is not None
    assert len(result["attempts"]) == 1
    assert result["attempts"][0].status == "SUCCESS"


def test_customer_approval_blocks_execution():

    orchestrator = RecoveryOrchestrator()

    result = orchestrator.run(
        transaction_id="TXN-002",
        intent=build_intent(),
        failed_product_id="P003",
        merchant_policy=build_policy(),
        customer_approved=False,
    )

    assert result["status"] == "CUSTOMER_APPROVAL_REQUIRED"
    assert result["selected_action"] is None
    assert result["attempts"][0].status == "BLOCKED"


def test_policy_blocks_action():

    orchestrator = RecoveryOrchestrator()

    restrictive_policy = MerchantPolicy(
        max_discount_percent=10,
        max_incentive_amount=500,
        allowed_actions=[],
    )

    result = orchestrator.run(
        transaction_id="TXN-003",
        intent=build_intent(),
        failed_product_id="P003",
        merchant_policy=restrictive_policy,
        customer_approved=True,
    )

    assert result["status"] == "RECOVERY_FAILED"
    assert result["selected_action"] is None
    assert len(result["attempts"]) > 0


def test_audit_trail_is_created():

    orchestrator = RecoveryOrchestrator()

    result = orchestrator.run(
        transaction_id="TXN-004",
        intent=build_intent(),
        failed_product_id="P003",
        merchant_policy=build_policy(),
        customer_approved=True,
    )

    event_types = [
        event.event_type
        for event in result["audit_events"]
    ]

    assert "RECOVERY_STARTED" in event_types
    assert "PLANS_GENERATED" in event_types
    assert "ACTION_PROPOSED" in event_types
    assert "POLICY_CHECK" in event_types
    assert "EXECUTION" in event_types
    assert "RECOVERY_COMPLETED" in event_types


def test_attempt_contains_transaction_identity():

    orchestrator = RecoveryOrchestrator()

    result = orchestrator.run(
        transaction_id="TXN-005",
        intent=build_intent(),
        failed_product_id="P003",
        merchant_policy=build_policy(),
        customer_approved=True,
    )

    attempt = result["attempts"][0]

    assert attempt.transaction_id == "TXN-005"
    assert attempt.attempt_id == "TXN-005-ATT-001"
    assert attempt.attempt_number == 1