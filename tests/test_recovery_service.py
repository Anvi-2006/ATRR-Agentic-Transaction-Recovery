from backend.app.models.transaction_intent import TransactionIntent
from backend.app.services.recovery_service import RecoveryService


def test_recovery_generates_alternative_products():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
    )

    service = RecoveryService()

    plans = service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P003",
    )

    assert len(plans) >= 1

    assert all(
        plan.action == "substitute_product"
        for plan in plans
    )


def test_failed_product_is_not_recommended():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryService()

    plans = service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P001",
    )

    assert all(
        plan.product_id != "P001"
        for plan in plans
    )


def test_invalid_products_are_not_recovery_options():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.5,
        delivery_deadline_days=1,
    )

    service = RecoveryService()

    plans = service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P001",
    )

    assert all(
        plan.constraint_safe
        for plan in plans
    )


def test_expected_margin_value_is_calculated():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryService()

    plans = service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P002",
    )

    for plan in plans:

        expected = (
            plan.expected_revenue
            * plan.merchant_margin_percent
            / 100
        )

        assert plan.expected_margin_value == expected


def test_recovery_plans_can_be_ranked():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = RecoveryService()

    plans = service.generate_recovery_plans(
        intent=intent,
        failed_product_id="P002",
    )

    ranked = service.rank_recovery_plans(plans)

    assert len(ranked) >= 1

    for i in range(len(ranked) - 1):
        assert (
            ranked[i].expected_margin_value
            >= ranked[i + 1].expected_margin_value
        )