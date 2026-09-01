from backend.app.agents.decision_agent import DecisionAgent
from backend.app.agents.agent_context import AgentContext

from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.execution_request import ExecutionRequest
from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.models.recovery_request import RecoveryRequest

from backend.app.services.recovery_service import RecoveryService
from backend.app.services.policy_service import PolicyService
from backend.app.services.execution_service import ExecutionService
from backend.app.services.audit_service import AuditService
from backend.app.services.replanning_service import ReplanningService
from backend.app.services.revenue_risk_service import RevenueRiskService


class RecoveryOrchestrator:

    def __init__(self):
        self.recovery_service = RecoveryService()
        self.policy_service = PolicyService()
        self.execution_service = ExecutionService()
        self.audit_service = AuditService()
        self.replanning_service = ReplanningService()
        self.revenue_risk_service = RevenueRiskService()
        self.decision_agent = DecisionAgent()

    def run(
        self,
        transaction_id: str,
        intent: TransactionIntent,
        failed_product_id: str,
        merchant_policy: MerchantPolicy,
        customer_approved: bool = True,
        simulation_mode: bool = False,
        simulation_scenario: str = "NORMAL",
    ) -> dict:

        attempts: list[RecoveryAttempt] = []

        # --------------------------------------------------
        # 1. Revenue risk detection
        # --------------------------------------------------

        risk_request = RecoveryRequest(
            transaction_id=transaction_id,
            failed_product_id=failed_product_id,
            category=intent.category,
            max_budget=intent.max_budget,
            min_rating=intent.min_rating,
            delivery_deadline_days=intent.delivery_deadline_days,
            customer_approved=customer_approved,
        )

        revenue_risk = self.revenue_risk_service.assess(
            request=risk_request,
            attempts=attempts,
        )

        self.audit_service.record(
            transaction_id=transaction_id,
            event_type="REVENUE_RISK_DETECTED",
            status=revenue_risk.risk_level,
            reason=revenue_risk.reason,
            metadata={
                "risk_score": revenue_risk.risk_score,
                "revenue_at_risk": revenue_risk.revenue_at_risk,
                "recoverable_revenue": revenue_risk.recoverable_revenue,
            },
        )

        # --------------------------------------------------
        # 2. START
        # --------------------------------------------------

        self.audit_service.record(
            transaction_id=transaction_id,
            event_type="RECOVERY_STARTED",
            status="STARTED",
            reason="ATRR recovery process started.",
        )

        # --------------------------------------------------
        # 3. DECISION + EXECUTION LOOP
        # --------------------------------------------------

        while True:

            # --------------------------------------------------
            # Generate a fresh intervention set on every loop.
            # This is what makes replanning adaptive.
            # --------------------------------------------------

            plans = self.recovery_service.generate_intervention_plans(
                intent=intent,
                failed_product_id=failed_product_id,
                merchant_policy=merchant_policy,
                previous_attempts=attempts,
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
                    ],
                    "interventions": [
                        plan.action
                        for plan in ranked_plans
                    ],
                    "expected_recovery_values": {
                        plan.plan_id: plan.expected_recovery_value
                        for plan in ranked_plans
                    },
                },
            )

            # --------------------------------------------------
            # 4. DECISION AGENT
            # --------------------------------------------------

            agent_context = AgentContext(
                transaction_id=transaction_id,
                intent=intent,
                recovery_plans=ranked_plans,
                merchant_policy=merchant_policy,
                previous_attempts=attempts,
                simulation_scenario=simulation_scenario,
            )

            agent_decision = self.decision_agent.decide(
                agent_context
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="AGENT_DECISION",
                status=agent_decision.decision,
                reason=agent_decision.reason,
                metadata={
                    "selected_plan_id": agent_decision.selected_plan_id,
                    "confidence": agent_decision.confidence,
                    "replanning_required": (
                        agent_decision.replanning_required
                    ),
                },
            )

            if agent_decision.decision == "ESCALATE":

                self.audit_service.record(
                    transaction_id=transaction_id,
                    event_type="RECOVERY_ESCALATED",
                    status="ESCALATED",
                    reason=agent_decision.reason,
                    metadata={
                        "confidence": agent_decision.confidence,
                        "attempt_count": len(attempts),
                    },
                )

                return {
                    "transaction_id": transaction_id,
                    "status": "ESCALATED",
                    "revenue_risk": revenue_risk,
                    "selected_action": None,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }


            if agent_decision.decision == "STOP":

                self.audit_service.record(
                    transaction_id=transaction_id,
                    event_type="RECOVERY_STOPPED",
                    status="STOPPED",
                    reason=agent_decision.reason,
                    metadata={
                        "stop_reason": agent_decision.stop_reason,
                    },
                )

                return {
                    "transaction_id": transaction_id,
                    "status": "RECOVERY_STOPPED",
                    "revenue_risk": revenue_risk,
                    "selected_action": None,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }


            if agent_decision.selected_plan_id is None:
                break

            selected_plan = next(
                (
                    plan
                    for plan in ranked_plans
                    if plan.plan_id
                    == agent_decision.selected_plan_id
                ),
                None,
            )

            if selected_plan is None:
                break

            # --------------------------------------------------
            # 5. PLAN -> ACTION
            # --------------------------------------------------

            action = RecoveryAction(
                action_id=selected_plan.plan_id,
                action_type=selected_plan.action,
                product_id=selected_plan.product_id,
                offer_id=selected_plan.offer_id,
                revenue_at_risk=selected_plan.expected_revenue,
                recoverable_revenue=selected_plan.expected_revenue,
                customer_cost=selected_plan.customer_cost,
                merchant_value=selected_plan.expected_margin_value,
                constraint_safe=selected_plan.constraint_safe,
                success_probability=selected_plan.success_probability,
                expected_recovery_value=(
                    selected_plan.expected_recovery_value
                ),
                reason=selected_plan.explanation,
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="ACTION_PROPOSED",
                action_id=action.action_id,
                status="PROPOSED",
                reason=action.reason,
                metadata={
                    "action_type": action.action_type,
                    "customer_cost": action.customer_cost,
                    "merchant_value": action.merchant_value,
                    "success_probability": (
                        action.success_probability
                    ),
                    "expected_recovery_value": (
                        action.expected_recovery_value
                    ),
                },
            )

            # --------------------------------------------------
            # 6. POLICY GATE
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
            # POLICY BLOCK -> REPLAN
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
                            f"{transaction_id}-ATT-"
                            f"{attempt_number:03d}"
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
            # 7. EXECUTION GATE
            # --------------------------------------------------

            execution_request = ExecutionRequest(
                action_id=action.action_id,
                policy_approved=policy_decision.allowed,
                customer_approved=customer_approved,
                simulation_mode=simulation_mode,
                attempt_number=len(attempts) + 1,
                simulation_scenario=simulation_scenario,
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
                            f"{transaction_id}-ATT-"
                            f"{attempt_number:03d}"
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
                    "revenue_risk": revenue_risk,
                    "selected_action": None,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }

            # --------------------------------------------------
            # 8. SUCCESS
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
                            f"{transaction_id}-ATT-"
                            f"{attempt_number:03d}"
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
                    metadata={
                        "revenue_recovered": min(
                            revenue_risk.revenue_at_risk,
                            action.recoverable_revenue,
                        )
                    },
                )

                return {
                    "transaction_id": transaction_id,
                    "status": "RECOVERED",
                    "revenue_risk": revenue_risk,
                    "selected_action": action,
                    "attempts": attempts,
                    "audit_events": (
                        self.audit_service
                        .get_transaction_events(transaction_id)
                    ),
                }

            # --------------------------------------------------
            # 9. EXECUTION FAILURE -> REPLAN
            # --------------------------------------------------

            attempt_number = (
                self.replanning_service.next_attempt_number(
                    attempts
                )
            )

            attempts.append(
                RecoveryAttempt(
                    attempt_id=(
                        f"{transaction_id}-ATT-"
                        f"{attempt_number:03d}"
                    ),
                    transaction_id=transaction_id,
                    action_id=action.action_id,
                    attempt_number=attempt_number,
                    status="FAILED",
                    reason=execution_result.reason,
                )
            )

            # Re-assess revenue risk after failure.
            revenue_risk = self.revenue_risk_service.assess(
                request=risk_request,
                attempts=attempts,
            )

            self.audit_service.record(
                transaction_id=transaction_id,
                event_type="REPLANNING_TRIGGERED",
                action_id=action.action_id,
                status="REPLANNING",
                reason=(
                    "Execution failed. "
                    "ATRR will regenerate and re-score "
                    "the available recovery interventions."
                ),
                metadata={
                    "updated_risk_score": revenue_risk.risk_score,
                    "updated_risk_level": revenue_risk.risk_level,
                },
            )

        # --------------------------------------------------
        # 10. NOTHING WORKED
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
            "revenue_risk": revenue_risk,
            "selected_action": None,
            "attempts": attempts,
            "audit_events": (
                self.audit_service
                .get_transaction_events(transaction_id)
            ),
        }
