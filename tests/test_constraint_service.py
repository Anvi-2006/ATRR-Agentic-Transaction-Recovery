from backend.app.models.transaction_intent import TransactionIntent
from backend.app.services.constraint_service import ConstraintService


def test_valid_product():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
        min_rating=4.0,
        delivery_deadline_days=2,
    )

    product = {
        "product_id": "P001",
        "price": "4499",
        "rating": "4.4",
    }

    inventory = {
        "available_quantity": "12"
    }

    delivery = {
        "standard_days": "2",
        "express_days": "1",
        "express_available": "true",
    }

    service = ConstraintService()

    result = service.evaluate_product(
        intent,
        product,
        inventory,
        delivery,
    )

    assert result.valid is True
    assert len(result.violations) == 0


def test_budget_violation():

    intent = TransactionIntent(
        category="headphones",
        max_budget=4000,
    )

    product = {
        "product_id": "P001",
        "price": "4499",
        "rating": "4.4",
    }

    inventory = {
        "available_quantity": "12"
    }

    delivery = {
        "standard_days": "2",
        "express_days": "1",
        "express_available": "true",
    }

    service = ConstraintService()

    result = service.evaluate_product(
        intent,
        product,
        inventory,
        delivery,
    )

    assert result.valid is False
    assert any(
        v.constraint == "max_budget"
        for v in result.violations
    )


def test_inventory_violation():

    intent = TransactionIntent(
        category="headphones",
        quantity=1,
    )

    product = {
        "product_id": "P002",
        "price": "4999",
        "rating": "4.6",
    }

    inventory = {
        "available_quantity": "0"
    }

    delivery = {
        "standard_days": "2",
        "express_days": "1",
        "express_available": "true",
    }

    service = ConstraintService()

    result = service.evaluate_product(
        intent,
        product,
        inventory,
        delivery,
    )

    assert result.valid is False
    assert any(
        v.constraint == "inventory"
        for v in result.violations
    )


def test_delivery_violation():

    intent = TransactionIntent(
        category="headphones",
        delivery_deadline_days=1,
    )

    product = {
        "product_id": "P003",
        "price": "3299",
        "rating": "4.1",
    }

    inventory = {
        "available_quantity": "8"
    }

    delivery = {
        "standard_days": "3",
        "express_days": "2",
        "express_available": "true",
    }

    service = ConstraintService()

    result = service.evaluate_product(
        intent,
        product,
        inventory,
        delivery,
    )

    assert result.valid is False
    assert any(
        v.constraint == "delivery_deadline"
        for v in result.violations
    )


def test_multiple_violations():

    intent = TransactionIntent(
        category="headphones",
        max_budget=3000,
        min_rating=4.5,
        delivery_deadline_days=1,
    )

    product = {
        "product_id": "P003",
        "price": "3299",
        "rating": "4.1",
    }

    inventory = {
        "available_quantity": "8"
    }

    delivery = {
        "standard_days": "3",
        "express_days": "2",
        "express_available": "true",
    }

    service = ConstraintService()

    result = service.evaluate_product(
        intent,
        product,
        inventory,
        delivery,
    )

    assert result.valid is False

    assert len(result.violations) == 3