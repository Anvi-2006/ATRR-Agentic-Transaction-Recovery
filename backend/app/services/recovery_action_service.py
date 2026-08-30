from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.transaction_intent import TransactionIntent
from backend.app.services.candidate_service import CandidateService


class RecoveryActionService:

    def __init__(self):
        self.candidate_service = CandidateService()

    def generate_substitution_actions(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
    ) -> list[RecoveryAction]:

        actions = []

        candidates = self.candidate_service.find_candidates(intent)

        for candidate in candidates:

            if candidate.product_id == failed_product_id:
                continue

            if not candidate.valid:
                continue

            merchant_value = (
                candidate.price
                * candidate.margin_percent
                / 100
            )

            actions.append(
                RecoveryAction(
                    action_id=f"SUB-{candidate.product_id}",
                    action_type="substitute_product",
                    product_id=candidate.product_id,
                    customer_cost=candidate.price,
                    merchant_value=merchant_value,
                    constraint_safe=True,
                    reason=(
                        f"{candidate.product_name} satisfies "
                        f"the customer's current constraints."
                    ),
                )
            )

        return actions