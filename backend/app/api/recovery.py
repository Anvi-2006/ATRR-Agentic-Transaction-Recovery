from fastapi import APIRouter

from backend.app.models.recovery_request import RecoveryRequest
from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy

from backend.app.services.recovery_orchestrator import (
    RecoveryOrchestrator,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Recovery"],
)


orchestrator = RecoveryOrchestrator()


@router.post("/recover")
def recover_transaction(request: RecoveryRequest):

    # -----------------------------------------
    # 1. Build transaction intent
    # -----------------------------------------

    intent = TransactionIntent(
        category=request.category,
        max_budget=request.max_budget,
        min_rating=request.min_rating,
        delivery_deadline_days=request.delivery_deadline_days,
    )

    # -----------------------------------------
    # 2. Merchant policy
    # -----------------------------------------

    merchant_policy = MerchantPolicy(
        max_discount_percent=10,
        max_incentive_amount=500,
        allowed_actions=[
            "substitute_product",
            "change_delivery",
            "offer_incentive",
        ],
    )

    # -----------------------------------------
    # 3. Run ATRR
    # -----------------------------------------

    result = orchestrator.run(
        transaction_id=request.transaction_id,
        intent=intent,
        failed_product_id=request.failed_product_id,
        merchant_policy=merchant_policy,
        customer_approved=request.customer_approved,
    )

    return result