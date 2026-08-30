from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.execution_request import ExecutionRequest
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.recovery_attempt import RecoveryAttempt

from backend.app.services.recovery_service import RecoveryService
from backend.app.services.policy_service import PolicyService
from backend.app.services.execution_service import ExecutionService
from backend.app.services.audit_service import AuditService
from backend.app.services.replanning_service import ReplanningService


class RecoveryOrchestrator:

    def __init__(self):
        self.recovery_service = RecoveryService()
        self.policy_service = PolicyService()
        self.execution_service = ExecutionService()
        self.audit_service = AuditService()
        self.replanning_service = ReplanningService()

    def run(
        self,
        transaction_id: str,
        intent: TransactionIntent,
        failed_product_id: str,
        merchant_policy: MerchantPolicy,
        customer_approved: bool = True,
    ) -> dict:

        attempts: list[RecoveryAttempt] = []

        # --------------------------------------------------
        # 1. START
        # --------------------------------------------------

        self.audit_service.record(
            transaction_id=transaction_id,
            event_type="RECOVERY_STARTED",
            status="STARTED",
            reason="ATRR recovery process started.",
        )

        # --------------------------------------------------
        # 2. GENERATE RECOVERY PLANS
        # --------------------------------------------------

        plans = self.recovery_service.generate_recovery_plans(
            intent=intent,
            failed_product_id=failed_product_id,
        )

        ranked_plans = self.recovery_service.rank_recovery_plans(
            plans
        )

        self.audit_service.record(
            transaction_id=transaction_id,
            event_type="PLANS_GENERATED",
            status="COMPLETED",
            reason=f"Generated {len(ranked_plans)} recovery plans.",
            metadata={
                "plan_ids": [
                    plan.plan_id
                    for plan in ranked_plans
                ]
            },
        )

        # --------------------------------------------------
        # 3. TRY PLANS IN RANKED ORDER
        # --------------------------------------------------

        for plan in ranked_plans:

            # Never retry an action that already failed
            available_ids = (
                self.replanning_service.filter_failed_actions(
                    action_ids=[
                        current_plan.plan_id
                        for current_plan in ranked_plans
                    ],
                    attempts=attempts,
                )
            )

            if plan.plan_id not in available_ids:
                continue

            # --------------------------------------------------
            # 4. PLAN → ACTION
            # --------------------------------------------------

            action = RecoveryAction(
                action_id=plan.plan_id,
                action_type=plan.action,
                product_id=plan.product_id,
                customer_cost=plan.customer_cost,
                merchant_value=plan.expected_margin_value,
                constraint_safe=plan.constraint_safe,
                reason=plan.explanation,
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="ACTION_PROPOSED",
                action_id=action.action_id,
                status="PROPOSED",
                reason=action.reason,
                metadata={
                    "customer_cost": action.customer_cost,
                    "merchant_value": action.merchant_value,
                },
            )

            # --------------------------------------------------
            # 5. POLICY GATE
            # --------------------------------------------------

            policy_decision = self.policy_service.evaluate(
                action=action,
                policy=merchant_policy,
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="POLICY_CHECK",
                action_id=action.action_id,
                status=(
                    "APPROVED"
                    if policy_decision.allowed
                    else "BLOCKED"
                ),
                reason=policy_decision.reason,
                metadata={
                    "policy_checks": policy_decision.policy_checks
                },
            )

            # --------------------------------------------------
            # POLICY BLOCK → REPLAN
            # --------------------------------------------------

            if not policy_decision.allowed:

                attempt_number = (
                    self.replanning_service.next_attempt_number(
                        attempts
                    )
                )

                attempts.append(
                    RecoveryAttempt(
                        attempt_id=(
                            f"{transaction_id}-ATT-{attempt_number:03d}"
                        ),
                        transaction_id=transaction_id,
                        action_id=action.action_id,
                        attempt_number=attempt_number,
                        status="FAILED",
                        reason=policy_decision.reason,
                    )
                )

                self.audit_service.record(
                    transaction_id=transaction_id,
                    event_type="REPLANNING_TRIGGERED",
                    action_id=action.action_id,
                    status="REPLANNING",
                    reason=(
                        "Recovery action blocked by policy. "
                        "Trying another safe plan."
                    ),
                )

                continue

            # --------------------------------------------------
            # 6. EXECUTION GATE
            # --------------------------------------------------

            execution_request = ExecutionRequest(
                action_id=action.action_id,
                policy_approved=policy_decision.allowed,
                customer_approved=customer_approved,
            )

            execution_result = self.execution_service.execute(
                execution_request
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="EXECUTION",
                action_id=action.action_id,
                status=execution_result.status,
                reason=execution_result.reason,
            )

            # --------------------------------------------------
            # CUSTOMER DID NOT APPROVE
            # --------------------------------------------------

            if not customer_approved:

                attempt_number = (
                    self.replanning_service.next_attempt_number(
                        attempts
                    )
                )

                attempts.append(
                    RecoveryAttempt(
                        attempt_id=(
                            f"{transaction_id}-ATT-{attempt_number:03d}"
                        ),
                        transaction_id=transaction_id,
                        action_id=action.action_id,
                        attempt_number=attempt_number,
                        status="BLOCKED",
                        reason=execution_result.reason,
                    )
                )

                self.audit_service.record(
                    transaction_id=transaction_id,
                    event_type="RECOVERY_STOPPED",
                    action_id=action.action_id,
                    status="BLOCKED",
                    reason=(
                        "Customer approval was not provided. "
                        "ATRR stopped without executing another action."
                    ),
                )

                return {
                    "transaction_id": transaction_id,
                    "status": "CUSTOMER_APPROVAL_REQUIRED",
                    "selected_action": None,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }

            # --------------------------------------------------
            # 7. SUCCESS
            # --------------------------------------------------

            if execution_result.executed:

                attempt_number = (
                    self.replanning_service.next_attempt_number(
                        attempts
                    )
                )

                attempts.append(
                    RecoveryAttempt(
                        attempt_id=(
                            f"{transaction_id}-ATT-{attempt_number:03d}"
                        ),
                        transaction_id=transaction_id,
                        action_id=action.action_id,
                        attempt_number=attempt_number,
                        status="SUCCESS",
                        reason=execution_result.reason,
                    )
                )

                self.audit_service.record(
                    transaction_id=transaction_id,
                    event_type="RECOVERY_COMPLETED",
                    action_id=action.action_id,
                    status="SUCCESS",
                    reason="Transaction successfully recovered.",
                )

                return {
                    "transaction_id": transaction_id,
                    "status": "RECOVERED",
                    "selected_action": action,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }

            # --------------------------------------------------
            # 8. EXECUTION FAILURE → REPLAN
            # --------------------------------------------------

            attempt_number = (
                self.replanning_service.next_attempt_number(
                    attempts
                )
            )

            attempts.append(
                RecoveryAttempt(
                    attempt_id=(
                        f"{transaction_id}-ATT-{attempt_number:03d}"
                    ),
                    transaction_id=transaction_id,
                    action_id=action.action_id,
                    attempt_number=attempt_number,
                    status="FAILED",
                    reason=execution_result.reason,
                )
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="REPLANNING_TRIGGERED",
                action_id=action.action_id,
                status="REPLANNING",
                reason=(
                    "Execution failed. "
                    "Searching for another safe recovery action."
                ),
            )

        # --------------------------------------------------
        # 9. NOTHING WORKED
        # --------------------------------------------------

        self.audit_service.record(
            transaction_id=transaction_id,
            event_type="RECOVERY_FAILED",
            status="FAILED",
            reason="No safe recovery plan could be executed.",
        )

        return {
            "transaction_id": transaction_id,
            "status": "RECOVERY_FAILED",
            "selected_action": None,
            "attempts": attempts,
            "audit_events": (
                self.audit_service
                .get_transaction_events(transaction_id)
            ),
        }