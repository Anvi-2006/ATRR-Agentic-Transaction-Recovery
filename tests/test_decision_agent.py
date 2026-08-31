from backend.app.agents.decision_agent import DecisionAgent
from backend.app.agents.agent_context import AgentContext

from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.services.recovery_service import RecoveryService


def build_context():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
    )

    policy = MerchantPolicy(
        max_discount_percent=10,
        max_incentive_amount=500,
        allowed_actions=[
            "substitute_product",
            "change_delivery",
            "offer_incentive",
        ],
    )

    recovery_service = RecoveryService()

    plans = recovery_service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P003",
    )

    ranked_plans = recovery_service.rank_recovery_plans(plans)

    return AgentContext(
        transaction_id="TXN-AGENT-001",
        intent=intent,
        recovery_plans=ranked_plans,
        merchant_policy=policy,
        previous_attempts=[],
    )


def test_agent_selects_recovery_plan():

    context = build_context()

    agent = DecisionAgent()

    decision = agent.decide(context)

    assert decision.selected_plan_id is not None
    assert decision.decision == "SELECT_RECOVERY_PLAN"
    assert decision.confidence > 0
    assert decision.replanning_required is False


def test_agent_does_not_repeat_failed_action():

    context = build_context()

    first_plan = context.recovery_plans[0]

    from backend.app.models.recovery_attempt import RecoveryAttempt

    context.previous_attempts = [
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-001",
            transaction_id="TXN-AGENT-001",
            action_id=first_plan.plan_id,
            attempt_number=1,
            status="FAILED",
            reason="Test failure",
        )
    ]

    agent = DecisionAgent()

    decision = agent.decide(context)

    assert decision.selected_plan_id != first_plan.plan_id


def test_agent_handles_no_plans():

    context = build_context()

    context.recovery_plans = []

    agent = DecisionAgent()

    decision = agent.decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "NO_RECOVERY_PLAN"