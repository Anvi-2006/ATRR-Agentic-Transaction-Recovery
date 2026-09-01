from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.models.revenue_risk import RevenueRisk
from backend.app.models.recovery_request import RecoveryRequest
from backend.app.services.merchant_data_service import MerchantDataService


class RevenueRiskService:

    HIGH_VALUE_THRESHOLD = 10000.0
    MEDIUM_VALUE_THRESHOLD = 5000.0

    def __init__(self):
        self.merchant_data = MerchantDataService()

    def assess(
        self,
        request: RecoveryRequest,
        attempts: list[RecoveryAttempt] | None = None,
    ) -> RevenueRisk:

        attempts = attempts or []

        product = self.merchant_data.get_product(
            request.failed_product_id
        )

        if product is None:
            return RevenueRisk(
                transaction_id=request.transaction_id,
                risk_level="LOW",
                risk_score=0.0,
                revenue_at_risk=0.0,
                recoverable_revenue=0.0,
                reason="Failed product could not be found.",
                recovery_eligible=False,
            )

        revenue_at_risk = float(product["price"])
        recoverable_revenue = revenue_at_risk

        failed_attempts = len(
            [
                attempt
                for attempt in attempts
                if attempt.status.upper() in {"FAILED", "BLOCKED"}
            ]
        )

        risk_score = 0.50

        if revenue_at_risk >= self.HIGH_VALUE_THRESHOLD:
            risk_score += 0.30
        elif revenue_at_risk >= self.MEDIUM_VALUE_THRESHOLD:
            risk_score += 0.20
        else:
            risk_score += 0.10

        risk_score += min(
            failed_attempts * 0.10,
            0.20,
        )

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.80:
            risk_level = "HIGH"
        elif risk_score >= 0.60:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        if failed_attempts:
            reason = (
                f"Revenue of ₹{revenue_at_risk:.2f} is at risk after "
                f"{failed_attempts} failed or blocked recovery attempt(s)."
            )
        else:
            reason = (
                f"Revenue of ₹{revenue_at_risk:.2f} is at risk because "
                f"the transaction failed and recovery is still available."
            )

        return RevenueRisk(
            transaction_id=request.transaction_id,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            revenue_at_risk=revenue_at_risk,
            recoverable_revenue=recoverable_revenue,
            reason=reason,
            recovery_eligible=True,
        )

    def assess_batch(
        self,
        requests: list[RecoveryRequest],
        attempts_by_transaction: dict[str, list[RecoveryAttempt]] | None = None,
    ) -> list[RevenueRisk]:

        attempts_by_transaction = attempts_by_transaction or {}

        return [
            self.assess(
                request=request,
                attempts=attempts_by_transaction.get(
                    request.transaction_id,
                    [],
                ),
            )
            for request in requests
        ]
