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
from backend.app.models.recovery_plan import RecoveryPlan
from backend.app.models.recovery_attempt import RecoveryAttempt


def build_custom_plan(
    plan_id="PLAN-001",
    expected_value=1000.0,
):
    return RecoveryPlan(
        plan_id=plan_id,
        action="payment_retry",
        product_id="P003",
        customer_cost=0.0,
        merchant_margin_percent=25.0,
        constraint_safe=True,
        expected_revenue=3299.0,
        expected_margin_value=824.75,
        success_probability=0.70,
        expected_recovery_value=expected_value,
        explanation="Test recovery plan.",
    )


def test_agent_escalates_when_all_actions_are_exhausted():

    context = build_context()

    first_plan = context.recovery_plans[0]

    context.previous_attempts = [
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-001",
            transaction_id="TXN-AGENT-001",
            action_id=first_plan.plan_id,
            attempt_number=1,
            status="FAILED",
            reason="Recovery action failed.",
        )
    ]

    context.recovery_plans = [first_plan]

    decision = DecisionAgent().decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "ESCALATE"
    assert decision.escalation_required is True


def test_agent_escalates_when_expected_value_is_too_low():

    context = build_context()

    context.merchant_policy.minimum_expected_recovery_value = 1000.0

    low_value_plan = build_custom_plan(
        plan_id="LOW-VALUE",
        expected_value=100.0,
    )

    context.recovery_plans = [low_value_plan]
    context.previous_attempts = []

    decision = DecisionAgent().decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "ESCALATE"
    assert decision.escalation_required is True
    assert decision.stop_reason is None


def test_agent_stops_when_low_value_and_escalation_disabled():

    context = build_context()

    context.merchant_policy.minimum_expected_recovery_value = 1000.0
    context.merchant_policy.allow_escalation = False

    low_value_plan = build_custom_plan(
        plan_id="LOW-VALUE-STOP",
        expected_value=100.0,
    )

    context.recovery_plans = [low_value_plan]
    context.previous_attempts = []

    decision = DecisionAgent().decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "STOP"
    assert decision.escalation_required is False
    assert decision.stop_reason == "LOW_EXPECTED_RECOVERY_VALUE"


def test_agent_escalates_after_max_automated_attempts():

    context = build_context()

    context.merchant_policy.max_automated_attempts = 2

    context.previous_attempts = [
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-001",
            transaction_id="TXN-AGENT-001",
            action_id="ATTEMPT-001",
            attempt_number=1,
            status="FAILED",
            reason="First attempt failed.",
        ),
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-002",
            transaction_id="TXN-AGENT-001",
            action_id="ATTEMPT-002",
            attempt_number=2,
            status="FAILED",
            reason="Second attempt failed.",
        ),
    ]

    decision = DecisionAgent().decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "ESCALATE"
    assert decision.escalation_required is True


def test_agent_stops_after_max_attempts_when_escalation_disabled():

    context = build_context()

    context.merchant_policy.max_automated_attempts = 2
    context.merchant_policy.allow_escalation = False

    context.previous_attempts = [
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-001",
            transaction_id="TXN-AGENT-001",
            action_id="ATTEMPT-001",
            attempt_number=1,
            status="FAILED",
            reason="First attempt failed.",
        ),
        RecoveryAttempt(
            attempt_id="TXN-AGENT-001-ATT-002",
            transaction_id="TXN-AGENT-001",
            action_id="ATTEMPT-002",
            attempt_number=2,
            status="FAILED",
            reason="Second attempt failed.",
        ),
    ]

    decision = DecisionAgent().decide(context)

    assert decision.selected_plan_id is None
    assert decision.decision == "STOP"
    assert decision.escalation_required is False
    assert decision.stop_reason == "MAX_AUTOMATED_ATTEMPTS"
