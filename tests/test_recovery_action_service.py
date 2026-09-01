from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy
from backend.app.services.recovery_action_service import (
    RecoveryActionService,
)


def test_substitution_action_is_generated():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
    )

    service = RecoveryActionService()

    actions = service.generate_substitution_actions(
        intent=intent,
        failed_product_id="P003",
    )

    assert len(actions) >= 1

    assert all(
        action.action_type == "substitute_product"
        for action in actions
    )


def test_failed_product_is_not_used():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryActionService()

    actions = service.generate_substitution_actions(
        intent=intent,
        failed_product_id="P001",
    )

    assert all(
        action.product_id != "P001"
        for action in actions
    )


def test_only_constraint_safe_actions_are_generated():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.5,
        delivery_deadline_days=1,
    )

    service = RecoveryActionService()

    actions = service.generate_substitution_actions(
        intent=intent,
        failed_product_id="P001",
    )

    assert all(
        action.constraint_safe is True
        for action in actions
    )


def test_merchant_value_is_positive():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryActionService()

    actions = service.generate_substitution_actions(
        intent=intent,
        failed_product_id="P002",
    )

    assert all(
        action.merchant_value > 0
        for action in actions
    )

def test_action_contains_reason():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryActionService()

    actions = service.generate_substitution_actions(
        intent=intent,
        failed_product_id="P002",
    )

    assert all(
        action.reason
        for action in actions
    )
def create_policy():
    return MerchantPolicy(
        max_discount_percent=15,
        max_incentive_amount=500,
        min_margin_percent=10,
        allow_product_substitution=True,
        allow_payment_retry=True,
        max_payment_retries=2,
        allowed_actions=[
            "substitute_product",
            "payment_retry",
            "offer_incentive",
            "change_delivery",
        ],
    )


def test_payment_retry_action_is_generated():

    intent = TransactionIntent(
        category="headphones",
    )

    service = RecoveryActionService()

    actions = service.generate_payment_retry_actions(
        intent=intent,
        failed_product_id="P003",
        policy=create_policy(),
    )

    assert len(actions) == 1
    assert actions[0].action_type == "payment_retry"
    assert actions[0].customer_cost == 0
    assert actions[0].success_probability == 0.0


def test_payment_retry_respects_retry_limit():

    intent = TransactionIntent(
        category="headphones",
    )

    service = RecoveryActionService()

    actions = service.generate_payment_retry_actions(
        intent=intent,
        failed_product_id="P003",
        policy=create_policy(),
        previous_retry_count=2,
    )

    assert actions == []


def test_offer_action_uses_existing_offer():

    intent = TransactionIntent(
        category="headphones",
    )

    service = RecoveryActionService()

    actions = service.generate_offer_actions(
        intent=intent,
        failed_product_id="P003",
        policy=create_policy(),
    )

    assert len(actions) >= 1
    assert all(
        action.action_type == "offer_incentive"
        for action in actions
    )
    assert all(
        action.offer_id
        for action in actions
    )


def test_delivery_action_is_generated_when_express_meets_deadline():

    intent = TransactionIntent(
        category="headphones",
        delivery_deadline_days=2,
    )

    service = RecoveryActionService()

    actions = service.generate_delivery_actions(
        intent=intent,
        failed_product_id="P003",
    )

    assert len(actions) == 1
    assert actions[0].action_type == "change_delivery"
    assert actions[0].constraint_safe is True


def test_incentive_respects_discount_policy():

    intent = TransactionIntent(
        category="headphones",
    )

    policy = create_policy()
    policy.max_discount_percent = 1

    service = RecoveryActionService()

    actions = service.generate_offer_actions(
        intent=intent,
        failed_product_id="P003",
        policy=policy,
    )

    assert actions == []


