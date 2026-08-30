from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.policy_decision import PolicyDecision


class PolicyService:

    def evaluate(
        self,
        action: RecoveryAction,
        policy: MerchantPolicy,
    ) -> PolicyDecision:

        action_allowed = (
            action.action_type in policy.allowed_actions
        )

        amount_within_limit = (
            action.customer_cost >= 0
        )

        constraint_safe = action.constraint_safe

        allowed = (
            action_allowed
            and amount_within_limit
            and constraint_safe
        )

        if not action_allowed:
            reason = "Recovery action is not allowed by merchant policy."

        elif not amount_within_limit:
            reason = "Transaction amount violates policy limits."

        elif not constraint_safe:
            reason = "Action violates customer constraints."

        else:
            reason = "Recovery action passed all policy checks."

        return PolicyDecision(
            allowed=allowed,
            reason=reason,
            policy_checks={
                "action_allowed": action_allowed,
                "amount_within_limit": amount_within_limit,
                "customer_constraint_safe": constraint_safe,
            },
        )