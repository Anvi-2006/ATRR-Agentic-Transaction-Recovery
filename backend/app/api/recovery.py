from fastapi import APIRouter, HTTPException

from backend.app.models.batch_recovery import (
    BatchRecoveryRequest,
)
from backend.app.models.recovery_request import RecoveryRequest
from backend.app.models.transaction_intent import TransactionIntent

from backend.app.services.recovery_orchestrator import (
    RecoveryOrchestrator,
)
from backend.app.services.merchant_data_service import (
    MerchantDataService,
)
from backend.app.services.batch_recovery_service import (
    BatchRecoveryService,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["Recovery"],
)


orchestrator = RecoveryOrchestrator()
merchant_data = MerchantDataService()
batch_service = BatchRecoveryService()


@router.post("/recover")
def recover_transaction(request: RecoveryRequest):

    intent = TransactionIntent(
        category=request.category,
        max_budget=request.max_budget,
        min_rating=request.min_rating,
        delivery_deadline_days=(
            request.delivery_deadline_days
        ),
    )

    merchant_policy = (
        merchant_data
        .get_merchant_policy_model("M001")
    )

    if merchant_policy is None:
        raise HTTPException(
            status_code=500,
            detail="Merchant policy could not be loaded.",
        )

    return orchestrator.run(
        transaction_id=request.transaction_id,
        intent=intent,
        failed_product_id=request.failed_product_id,
        merchant_policy=merchant_policy,
        customer_approved=request.customer_approved,
    )


@router.post("/recover/batch")
def recover_batch(request: BatchRecoveryRequest):

    try:
        return batch_service.process(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
