from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.models.recovery_action import RecoveryAction
from backend.app.services.policy_service import PolicyService


def create_action():

    return RecoveryAction(
        action_id="SUB-P001",
        action_type="substitute_product",
        product_id="P001",
        customer_cost=4499,
        merchant_value=809.82,
        constraint_safe=True,
        reason="Valid alternative product.",
    )


def create_policy():

    return MerchantPolicy(
        max_discount_percent=10,
        max_incentive_amount=500,
        allowed_actions=[
            "substitute_product",
            "change_delivery",
            "offer_incentive",
        ],
    )


def test_allowed_action():

    service = PolicyService()

    decision = service.evaluate(
        create_action(),
        create_policy(),
    )

    assert decision.allowed is True


def test_disallowed_action():

    service = PolicyService()

    policy = create_policy()

    policy.allowed_actions = []

    decision = service.evaluate(
        create_action(),
        policy,
    )

    assert decision.allowed is False


def test_constraint_violation_is_rejected():

    service = PolicyService()

    action = create_action()
    action.constraint_safe = False

    decision = service.evaluate(
        action,
        create_policy(),
    )

    assert decision.allowed is False


def test_policy_checks_are_returned():

    service = PolicyService()

    decision = service.evaluate(
        create_action(),
        create_policy(),
    )

    assert "action_allowed" in decision.policy_checks
    assert "amount_within_limit" in decision.policy_checks
    assert "customer_constraint_safe" in decision.policy_checks


def test_explanation_is_returned():

    service = PolicyService()

    decision = service.evaluate(
        create_action(),
        create_policy(),
    )

    assert decision.reason