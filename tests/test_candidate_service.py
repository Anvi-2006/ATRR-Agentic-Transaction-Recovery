from backend.app.models.transaction_intent import TransactionIntent
from backend.app.services.candidate_service import CandidateService


def test_candidate_search_returns_headphones():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = CandidateService()

    candidates = service.find_candidates(intent)

    assert len(candidates) == 4


def test_candidate_contains_product_information():

    intent = TransactionIntent(
        category="headphones",
    )

    service = CandidateService()

    candidates = service.find_candidates(intent)

    p001 = next(
        candidate
        for candidate in candidates
        if candidate.product_id == "P001"
    )

    assert p001.product_name == "SoundMax Wireless Headphones"
    assert p001.price == 4499
    assert p001.rating == 4.4


def test_out_of_stock_product_is_invalid():

    intent = TransactionIntent(
        category="headphones",
    )

    service = CandidateService()

    candidates = service.find_candidates(intent)

    p002 = next(
        candidate
        for candidate in candidates
        if candidate.product_id == "P002"
    )

    assert p002.available_quantity == 0
    assert p002.valid is False


def test_budget_filters_candidate_validity():

    intent = TransactionIntent(
        category="headphones",
        max_budget=5000,
    )

    service = CandidateService()

    candidates = service.find_candidates(intent)

    p004 = next(
        candidate
        for candidate in candidates
        if candidate.product_id == "P004"
    )

    assert p004.price == 5799
    assert p004.valid is False


def test_category_filter():

    intent = TransactionIntent(
        category="earbuds",
    )

    service = CandidateService()

    candidates = service.find_candidates(intent)

    assert len(candidates) == 1
    assert candidates[0].product_id == "P005"