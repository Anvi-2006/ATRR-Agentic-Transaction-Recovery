from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.models.recovery_intervention import RecoveryIntervention

from backend.app.services.candidate_service import CandidateService
from backend.app.services.merchant_data_service import MerchantDataService
from backend.app.services.recovery_action_service import RecoveryActionService
from backend.app.services.recovery_outcome_service import RecoveryOutcomeService
from backend.app.services.recovery_value_service import RecoveryValueService


class RecoveryService:

    def __init__(self):
        self.candidate_service = CandidateService()
        self.merchant_data = MerchantDataService()
        self.action_service = RecoveryActionService()
        self.outcome_service = RecoveryOutcomeService()
        self.value_service = RecoveryValueService()

    # --------------------------------------------------
    # Legacy substitution-only planner
    # --------------------------------------------------

    def generate_recovery_plans(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
    ) -> list[RecoveryPlan]:

        plans = []

        candidates = self.candidate_service.find_candidates(intent)

        for candidate in candidates:

            if candidate.product_id == failed_product_id:
                continue

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
                    success_probability=0.0,
                    expected_recovery_value=0.0,
                    explanation=(
                        f"Substitute failed product with "
                        f"{candidate.product_name} because it "
                        f"satisfies the customer's constraints."
                    ),
                )
            )

        return plans

    # --------------------------------------------------
    # Track 03 multi-intervention planner
    # --------------------------------------------------

    def generate_intervention_plans(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
        merchant_policy: MerchantPolicy,
        previous_attempts: list[RecoveryAttempt] | None = None,
    ) -> list[RecoveryPlan]:

        previous_attempts = previous_attempts or []

        attempted_action_ids = {
            attempt.action_id
            for attempt in previous_attempts
        }

        retry_count = sum(
            1
            for attempt in previous_attempts
            if attempt.action_id.startswith("RETRY-")
        )

        actions = []

        # --------------------------------------------------
        # 1. Product substitution
        # --------------------------------------------------

        actions.extend(
            self.action_service.generate_substitution_actions(
                intent=intent,
                failed_product_id=failed_product_id,
            )
        )

        # --------------------------------------------------
        # 2. Payment retry
        # --------------------------------------------------

        actions.extend(
            self.action_service.generate_payment_retry_actions(
                intent=intent,
                failed_product_id=failed_product_id,
                policy=merchant_policy,
                previous_retry_count=retry_count,
            )
        )

        # --------------------------------------------------
        # 3. Offer / incentive
        # --------------------------------------------------

        actions.extend(
            self.action_service.generate_offer_actions(
                intent=intent,
                failed_product_id=failed_product_id,
                policy=merchant_policy,
            )
        )

        # --------------------------------------------------
        # 4. Delivery change
        # --------------------------------------------------

        actions.extend(
            self.action_service.generate_delivery_actions(
                intent=intent,
                failed_product_id=failed_product_id,
            )
        )

        # --------------------------------------------------
        # Remove interventions already attempted
        # --------------------------------------------------

        actions = [
            action
            for action in actions
            if action.action_id not in attempted_action_ids
        ]

        # --------------------------------------------------
        # Estimate outcome for every action
        # --------------------------------------------------

        outcomes = self.outcome_service.estimate_batch(
            actions=actions,
            previous_attempts=previous_attempts,
        )

        outcome_by_action_id = {
            outcome.intervention_id: outcome
            for outcome in outcomes
        }

        # --------------------------------------------------
        # Convert actions into scored interventions
        # --------------------------------------------------

        interventions = []

        for action in actions:

            product = None

            if action.product_id:
                product = self.merchant_data.get_product(
                    action.product_id
                )

            revenue_at_risk = action.revenue_at_risk
            recoverable_revenue = action.recoverable_revenue
            merchant_cost = 0.0

            if action.action_type == "offer_incentive":
                merchant_cost = action.customer_cost

            outcome = outcome_by_action_id[action.action_id]

            interventions.append(
                RecoveryIntervention(
                    intervention_id=action.action_id,
                    intervention_type=action.action_type,
                    product_id=action.product_id,
                    offer_id=action.offer_id,
                    revenue_at_risk=revenue_at_risk,
                    recoverable_revenue=recoverable_revenue,
                    customer_cost=action.customer_cost,
                    merchant_cost=merchant_cost,
                    success_probability=outcome.success_probability,
                    constraint_safe=action.constraint_safe,
                    policy_safe=(
                        action.action_type
                        in merchant_policy.allowed_actions
                    ),
                    reason=(
                        f"{action.reason} "
                        f"Outcome estimate: {outcome.explanation}"
                    ),
                )
            )

        # --------------------------------------------------
        # Score interventions
        # --------------------------------------------------

        scored_interventions = self.value_service.score(
            interventions
        )

        # --------------------------------------------------
        # Convert scored interventions into RecoveryPlan
        # --------------------------------------------------

        plans = []

        for intervention in scored_interventions:

            action = next(
                (
                    item
                    for item in actions
                    if item.action_id
                    == intervention.intervention_id
                ),
                None,
            )

            if action is None:
                continue

            product = None

            if action.product_id:
                product = self.merchant_data.get_product(
                    action.product_id
                )

            margin_percent = (
                float(product["margin_percent"])
                if product is not None
                else 0.0
            )

            expected_revenue = (
                intervention.recoverable_revenue
            )

            expected_margin_value = (
                expected_revenue
                * margin_percent
                / 100
            )

            outcome = outcome_by_action_id[
                action.action_id
            ]

            plans.append(
                RecoveryPlan(
                    plan_id=action.action_id,
                    action=action.action_type,
                    product_id=action.product_id,
                    offer_id=action.offer_id,
                    customer_cost=action.customer_cost,
                    merchant_margin_percent=margin_percent,
                    constraint_safe=(
                        action.constraint_safe
                        and intervention.policy_safe
                    ),
                    expected_revenue = intervention.recoverable_revenue,
                    expected_margin_value=expected_margin_value,
                    success_probability=(
                        outcome.success_probability
                    ),
                    expected_recovery_value=(
                        intervention.expected_recovery_value
                    ),
                    explanation=(
                        f"{action.reason} "
                        f"{outcome.explanation}"
                    ),
                    metadata={
                        "outcome_confidence": outcome.confidence,
                        "risk_adjusted": True,
                    },
                )
            )

        return plans

    def rank_recovery_plans(
        self,
        plans: list[RecoveryPlan],
    ) -> list[RecoveryPlan]:

        return sorted(
            plans,
            key=lambda plan: (
                plan.expected_recovery_value
                if plan.expected_recovery_value > 0
                else plan.expected_margin_value
            ),
            reverse=True,
        )