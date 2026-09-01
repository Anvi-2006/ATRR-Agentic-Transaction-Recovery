from backend.app.agents.agent_context import AgentContext
from backend.app.models.agent_decision import AgentDecision


class DecisionAgent:

    def decide(self, context: AgentContext) -> AgentDecision:
        if context.simulation_scenario == "STOP":
            return AgentDecision(
                selected_plan_id=None,
                decision="STOP",
                confidence=1.0,
                reason=(
                    "Simulation stop scenario requested. "
                    "ATRR will not execute a recovery action."
                ),
                replanning_required=False,
                escalation_required=False,
                stop_reason="SIMULATION_STOP",
            )
        # --------------------------------------------------
        # 1. No recovery plans
        # --------------------------------------------------

        if not context.recovery_plans:

            return AgentDecision(
                selected_plan_id=None,
                decision="NO_RECOVERY_PLAN",
                confidence=1.0,
                reason="No recovery plans are available.",
                replanning_required=False,
                escalation_required=False,
                stop_reason="NO_RECOVERY_PLAN",
            )

        # --------------------------------------------------
        # 2. Remove previously attempted actions
        # --------------------------------------------------

        attempted_actions = {
            attempt.action_id
            for attempt in context.previous_attempts
        }

        available_plans = [
            plan
            for plan in context.recovery_plans
            if plan.plan_id not in attempted_actions
        ]

        # --------------------------------------------------
        # 3. No unattempted plans remain
        # --------------------------------------------------

        if not available_plans:

            if context.merchant_policy.allow_escalation:

                return AgentDecision(
                    selected_plan_id=None,
                    decision="ESCALATE",
                    confidence=0.95,
                    reason=(
                        "All available recovery actions have "
                        "already been attempted. Escalation is "
                        "permitted by merchant policy."
                    ),
                    replanning_required=False,
                    escalation_required=True,
                    stop_reason=None,
                )

            return AgentDecision(
                selected_plan_id=None,
                decision="STOP",
                confidence=1.0,
                reason=(
                    "All available recovery plans have already "
                    "been attempted."
                ),
                replanning_required=False,
                escalation_required=False,
                stop_reason="ALL_ACTIONS_ATTEMPTED",
            )

        # --------------------------------------------------
        # 4. Automated attempt limit
        # --------------------------------------------------

        if (
            len(context.previous_attempts)
            >= context.merchant_policy.max_automated_attempts
        ):

            if context.merchant_policy.allow_escalation:

                return AgentDecision(
                    selected_plan_id=None,
                    decision="ESCALATE",
                    confidence=0.95,
                    reason=(
                        "The maximum number of automated recovery "
                        "attempts has been reached. Escalation is "
                        "required by the recovery guardrails."
                    ),
                    replanning_required=False,
                    escalation_required=True,
                    stop_reason=None,
                )

            return AgentDecision(
                selected_plan_id=None,
                decision="STOP",
                confidence=1.0,
                reason=(
                    "The maximum number of automated recovery "
                    "attempts has been reached."
                ),
                replanning_required=False,
                escalation_required=False,
                stop_reason="MAX_AUTOMATED_ATTEMPTS",
            )

        # --------------------------------------------------
        # 5. Rank available plans by expected recovery value
        # --------------------------------------------------

        def decision_score(plan):

            if plan.expected_recovery_value > 0:
                return plan.expected_recovery_value

            return plan.expected_margin_value

        available_plans.sort(
            key=decision_score,
            reverse=True,
        )

        selected_plan = available_plans[0]

        selected_score = decision_score(
            selected_plan
        )

        # --------------------------------------------------
        # 6. Minimum expected recovery value guardrail
        # --------------------------------------------------

        if (
            selected_score
            < context.merchant_policy.minimum_expected_recovery_value
        ):

            if context.merchant_policy.allow_escalation:

                return AgentDecision(
                    selected_plan_id=None,
                    decision="ESCALATE",
                    confidence=0.90,
                    reason=(
                        f"The best available recovery plan has "
                        f"an expected recovery value of "
                        f"{selected_score:.2f}, which is below "
                        f"the merchant's minimum acceptable "
                        f"value of "
                        f"{context.merchant_policy.minimum_expected_recovery_value:.2f}."
                    ),
                    replanning_required=False,
                    escalation_required=True,
                    stop_reason=None,
                )

            return AgentDecision(
                selected_plan_id=None,
                decision="STOP",
                confidence=0.95,
                reason=(
                    f"The best available recovery plan has "
                    f"an expected recovery value of "
                    f"{selected_score:.2f}, below the merchant "
                    f"minimum of "
                    f"{context.merchant_policy.minimum_expected_recovery_value:.2f}."
                ),
                replanning_required=False,
                escalation_required=False,
                stop_reason="LOW_EXPECTED_RECOVERY_VALUE",
            )

        # --------------------------------------------------
        # 7. Calculate decision confidence
        # --------------------------------------------------

        confidence = 0.70

        if selected_plan.expected_recovery_value > 0:

            confidence = min(
                0.99,
                0.70
                + (
                    selected_plan.success_probability
                    * 0.25
                ),
            )

        # --------------------------------------------------
        # 8. Normal recovery decision
        # --------------------------------------------------

        return AgentDecision(
            selected_plan_id=selected_plan.plan_id,
            decision="SELECT_RECOVERY_PLAN",
            confidence=round(
                confidence,
                2,
            ),
            reason=(
                f"Selected {selected_plan.plan_id} because it "
                f"has the highest expected recovery value among "
                f"available recovery plans "
                f"({selected_score:.2f}) while satisfying the "
                f"current recovery guardrails."
            ),
            replanning_required=False,
            escalation_required=False,
            stop_reason=None,
        )
