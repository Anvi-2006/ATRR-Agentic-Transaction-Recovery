from backend.app.agents.agent_context import AgentContext
from backend.app.models.agent_decision import AgentDecision


class DecisionAgent:

    def decide(self, context: AgentContext) -> AgentDecision:

        if not context.recovery_plans:

            return AgentDecision(
                selected_plan_id=None,
                decision="NO_RECOVERY_PLAN",
                confidence=1.0,
                reason="No recovery plans are available.",
                replanning_required=False,
            )

        attempted_actions = {
            attempt.action_id
            for attempt in context.previous_attempts
        }

        available_plans = [
            plan
            for plan in context.recovery_plans
            if plan.plan_id not in attempted_actions
        ]

        if not available_plans:

            return AgentDecision(
                selected_plan_id=None,
                decision="NO_AVAILABLE_ACTION",
                confidence=1.0,
                reason="All available recovery plans have already been attempted.",
                replanning_required=False,
            )

        selected_plan = available_plans[0]

        return AgentDecision(
            selected_plan_id=selected_plan.plan_id,
            decision="SELECT_RECOVERY_PLAN",
            confidence=0.90,
            reason=(
                f"Selected {selected_plan.plan_id} as the next recovery "
                "plan because it is the highest-ranked available option "
                "that satisfies the current recovery constraints."
            ),
            replanning_required=False,
        )