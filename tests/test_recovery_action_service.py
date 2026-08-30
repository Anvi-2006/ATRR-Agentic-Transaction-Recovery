from backend.app.models.transaction_intent import TransactionIntent
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