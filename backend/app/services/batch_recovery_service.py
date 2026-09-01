from backend.app.models.batch_recovery import (
    BatchRecoveryMetrics,
    BatchRecoveryResponse,
    BatchRecoveryRequest,
)

from backend.app.models.transaction_intent import TransactionIntent
from backend.app.services.recovery_orchestrator import RecoveryOrchestrator
from backend.app.services.merchant_data_service import MerchantDataService


class BatchRecoveryService:

    def __init__(self):
        self.orchestrator = RecoveryOrchestrator()
        self.merchant_data = MerchantDataService()

    def process(
        self,
        request: BatchRecoveryRequest,
    ) -> BatchRecoveryResponse:

        results = []

        transactions_evaluated = len(
            request.transactions
        )

        transactions_recovered = 0
        transactions_failed = 0
        transactions_blocked = 0
        transactions_replanned = 0
        transactions_escalated = 0
        transactions_stopped = 0
        recovery_eligible = 0
        
        

        revenue_at_risk = 0.0
        revenue_recovered = 0.0

        merchant_policy = (
            self.merchant_data
            .get_merchant_policy_model("M001")
        )

        if merchant_policy is None:
            raise ValueError(
                "Merchant policy could not be loaded."
            )

        for transaction in request.transactions:

            intent = TransactionIntent(
                category=transaction.category,
                max_budget=transaction.max_budget,
                min_rating=transaction.min_rating,
                delivery_deadline_days=(
                    transaction.delivery_deadline_days
                ),
            )

            result = self.orchestrator.run(
                transaction_id=transaction.transaction_id,
                intent=intent,
                failed_product_id=(
                    transaction.failed_product_id
                ),
                merchant_policy=merchant_policy,
                customer_approved=(
                    transaction.customer_approved
                ),
                simulation_mode=request.simulation_mode,
                simulation_scenario=(
                    transaction.simulation_scenario
                ),
            )

            results.append(result)
            if len(result.get("attempts", [])) > 1:
                transactions_replanned += 1

            risk = result.get("revenue_risk")

            if risk is not None:

                if risk.recovery_eligible:
                    recovery_eligible += 1

                revenue_at_risk += (
                    risk.revenue_at_risk
                )

            status = result.get("status")

            if status == "RECOVERED":

                transactions_recovered += 1

                if risk is not None:

                    recovered = min(
                        risk.revenue_at_risk,
                        risk.recoverable_revenue,
                    )

                    revenue_recovered += recovered

            elif status == "CUSTOMER_APPROVAL_REQUIRED":

                transactions_blocked += 1

            elif status == "ESCALATED":

                transactions_escalated += 1

            elif status == "RECOVERY_STOPPED":

                transactions_stopped += 1

            else:

                transactions_failed += 1

        recovery_rate = (
            transactions_recovered
            / transactions_evaluated
            if transactions_evaluated
            else 0.0
        )

        revenue_recovery_rate = (
            revenue_recovered
            / revenue_at_risk
            if revenue_at_risk
            else 0.0
        )

        metrics = BatchRecoveryMetrics(
            transactions_evaluated=(
                transactions_evaluated
            ),
            recovery_eligible=recovery_eligible,
            transactions_recovered=(
                transactions_recovered
            ),
            transactions_failed=(
                transactions_failed
            ),
            transactions_blocked=(
                transactions_blocked
            ),
            transactions_escalated=(
                transactions_escalated
            ),
            transactions_stopped=(
                transactions_stopped
            ),
            revenue_at_risk=round(
                revenue_at_risk,
                2,
            ),
            revenue_recovered=round(
                revenue_recovered,
                2,
            ),
            recovery_rate=round(
                recovery_rate,
                4,
            ),
            revenue_recovery_rate=round(
                revenue_recovery_rate,
                4,
            ),
            transactions_replanned=transactions_replanned,
        )

        return BatchRecoveryResponse(
            metrics=metrics,
            results=results,
        )
