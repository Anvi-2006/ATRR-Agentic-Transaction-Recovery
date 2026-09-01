from backend.app.models.batch_recovery import BatchRecoveryRequest
from backend.app.models.recovery_request import RecoveryRequest
from backend.app.services.batch_recovery_service import (
    BatchRecoveryService,
)


def test_batch_recovery_returns_metrics():

    request = BatchRecoveryRequest(
        transactions=[
            RecoveryRequest(
                transaction_id="BATCH-001",
                failed_product_id="P003",
                category="headphones",
                max_budget=5000,
                min_rating=4.0,
                delivery_deadline_days=2,
                customer_approved=True,
            ),
            RecoveryRequest(
                transaction_id="BATCH-002",
                failed_product_id="P001",
                category="headphones",
                max_budget=5000,
                min_rating=4.0,
                delivery_deadline_days=2,
                customer_approved=True,
            ),
        ]
    )

    service = BatchRecoveryService()

    result = service.process(request)

    assert result.metrics.transactions_evaluated == 2
    assert result.metrics.revenue_at_risk > 0
    assert result.metrics.revenue_recovered >= 0

    assert (
        result.metrics.transactions_recovered
        + result.metrics.transactions_failed
        + result.metrics.transactions_blocked
        == 2
    )

    assert 0 <= result.metrics.recovery_rate <= 1
    assert 0 <= result.metrics.revenue_recovery_rate <= 1

    assert len(result.results) == 2

def test_batch_simulation_mode_is_supported():

    request = BatchRecoveryRequest(
        simulation_mode=True,
        transactions=[
            RecoveryRequest(
                transaction_id="BATCH-SIM-001",
                failed_product_id="P003",
                category="headphones",
                max_budget=5000,
                min_rating=4.0,
                delivery_deadline_days=2,
                customer_approved=True,
            )
        ],
    )

    service = BatchRecoveryService()

    result = service.process(request)

    assert result.metrics.transactions_evaluated == 1
    assert len(result.results) == 1
    assert result.results[0]["status"] in {
        "RECOVERED",
        "RECOVERY_FAILED",
        "CUSTOMER_APPROVAL_REQUIRED",
    }
