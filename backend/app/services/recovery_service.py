from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.services.candidate_service import CandidateService
from backend.app.services.merchant_data_service import MerchantDataService


class RecoveryService:

    def __init__(self):
        self.candidate_service = CandidateService()
        self.merchant_data = MerchantDataService()

    def generate_recovery_plans(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
    ) -> list[RecoveryPlan]:

        plans = []

        candidates = self.candidate_service.find_candidates(intent)

        for candidate in candidates:

            # Do not recommend the product that already failed
            if candidate.product_id == failed_product_id:
                continue

            # Only create executable plans for valid candidates
            if not candidate.valid:
                continue

            expected_revenue = candidate.price

            expected_margin_value = (
                expected_revenue
                * candidate.margin_percent
                / 100
            )

            plans.append(
                RecoveryPlan(
                    plan_id=f"SUB-{candidate.product_id}",
                    action="substitute_product",
                    product_id=candidate.product_id,
                    customer_cost=candidate.price,
                    merchant_margin_percent=candidate.margin_percent,
                    constraint_safe=True,
                    expected_revenue=expected_revenue,
                    expected_margin_value=expected_margin_value,
                    explanation=(
                        f"Substitute failed product with "
                        f"{candidate.product_name} because it "
                        f"satisfies the customer's constraints."
                    ),
                )
            )

        return plans

    def rank_recovery_plans(
        self,
        plans: list[RecoveryPlan],
    ) -> list[RecoveryPlan]:

        return sorted(
            plans,
            key=lambda plan: plan.expected_margin_value,
            reverse=True,
        )