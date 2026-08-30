import pytest

from backend.app.models.transaction_intent import TransactionIntent


def test_valid_transaction_intent():
    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.2,
        delivery_deadline_days=1,
        hard_constraints=[
            "max_budget",
            "delivery_deadline_days"
        ],
        soft_preferences=[
            "min_rating"
        ]
    )

    assert intent.category == "headphones"
    assert intent.max_budget == 5000
    assert intent.min_rating == 4.2
    assert intent.delivery_deadline_days == 1


def test_category_is_normalized():
    intent = TransactionIntent(
        category="  HEADPHONES  "
    )

    assert intent.category == "headphones"


def test_invalid_budget():
    with pytest.raises(ValueError):
        TransactionIntent(
            category="headphones",
            max_budget=0
        )


def test_invalid_rating():
    with pytest.raises(ValueError):
        TransactionIntent(
            category="headphones",
            min_rating=6
        )


def test_invalid_quantity():
    with pytest.raises(ValueError):
        TransactionIntent(
            category="headphones",
            quantity=0
        )