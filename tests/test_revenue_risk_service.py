from backend.app.models.recovery_request import RecoveryRequest
from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.services.revenue_risk_service import RevenueRiskService


def test_revenue_risk_is_detected_for_valid_failed_transaction():

    request = RecoveryRequest(
        transaction_id="TXN-RISK-001",
        failed_product_id="P003",
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
        customer_approved=True,
    )

    service = RevenueRiskService()

    risk = service.assess(request)

    assert risk.transaction_id == "TXN-RISK-001"
    assert risk.recovery_eligible is True
    assert risk.revenue_at_risk == 3299.0
    assert risk.recoverable_revenue == 3299.0
    assert 0 <= risk.risk_score <= 1
    assert risk.risk_level in {"LOW", "MEDIUM", "HIGH"}


def test_revenue_risk_is_increased_after_failed_attempts():

    request = RecoveryRequest(
        transaction_id="TXN-RISK-002",
        failed_product_id="P003",
        category="headphones",
        max_budget=5000,
        customer_approved=True,
    )

    service = RevenueRiskService()

    baseline = service.assess(request)

    attempts = [
        RecoveryAttempt(
            attempt_id="ATT-001",
            transaction_id="TXN-RISK-002",
            action_id="SUB-P001",
            attempt_number=1,
            status="FAILED",
            reason="Execution failed.",
        ),
        RecoveryAttempt(
            attempt_id="ATT-002",
            transaction_id="TXN-RISK-002",
            action_id="SUB-P004",
            attempt_number=2,
            status="FAILED",
            reason="Execution failed again.",
        ),
    ]

    updated = service.assess(
        request=request,
        attempts=attempts,
    )

    assert updated.risk_score > baseline.risk_score
    assert "2 failed or blocked recovery attempt(s)" in updated.reason


def test_missing_product_is_not_recovery_eligible():

    request = RecoveryRequest(
        transaction_id="TXN-RISK-003",
        failed_product_id="UNKNOWN",
        category="headphones",
        customer_approved=True,
    )

    service = RevenueRiskService()

    risk = service.assess(request)

    assert risk.recovery_eligible is False
    assert risk.revenue_at_risk == 0.0
    assert risk.recoverable_revenue == 0.0


def test_batch_revenue_risk_assessment():

    requests = [
        RecoveryRequest(
            transaction_id="TXN-RISK-004",
            failed_product_id="P003",
            category="headphones",
            customer_approved=True,
        ),
        RecoveryRequest(
            transaction_id="TXN-RISK-005",
            failed_product_id="P001",
            category="headphones",
            customer_approved=True,
        ),
    ]

    service = RevenueRiskService()

    results = service.assess_batch(requests)

    assert len(results) == 2
    assert results[0].transaction_id == "TXN-RISK-004"
    assert results[1].transaction_id == "TXN-RISK-005"
    assert all(result.recovery_eligible for result in results)
