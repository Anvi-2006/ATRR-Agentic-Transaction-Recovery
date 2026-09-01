from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.merchant_policy import MerchantPolicy

from backend.app.services.candidate_service import CandidateService
from backend.app.services.merchant_data_service import MerchantDataService


class RecoveryActionService:

    def __init__(self):
        self.candidate_service = CandidateService()
        self.merchant_data = MerchantDataService()

    def generate_substitution_actions(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
    ) -> list[RecoveryAction]:

        actions = []

        failed_product = self.merchant_data.get_product(
            failed_product_id
        )

        revenue_at_risk = (
            float(failed_product["price"])
            if failed_product
            else 0.0
        )

        candidates = self.candidate_service.find_candidates(intent)

        for candidate in candidates:

            if candidate.product_id == failed_product_id:
                continue

            if not candidate.valid:
                continue

            merchant_value = (
                candidate.price
                * candidate.margin_percent
                / 100
            )

            actions.append(
                RecoveryAction(
                    action_id=f"SUB-{candidate.product_id}",
                    action_type="substitute_product",
                    product_id=candidate.product_id,
                    revenue_at_risk=revenue_at_risk,
                    recoverable_revenue=min(
                        revenue_at_risk,
                        candidate.price,
                    ),
                    customer_cost=candidate.price,
                    merchant_value=merchant_value,
                    constraint_safe=True,
                    success_probability=0.0,
                    expected_recovery_value=0.0,
                    reason=(
                        f"{candidate.product_name} satisfies "
                        f"the customer's current constraints."
                    ),
                )
            )

        return actions

    def generate_payment_retry_actions(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
        policy: MerchantPolicy,
        previous_retry_count: int = 0,
    ) -> list[RecoveryAction]:

        if not policy.allow_payment_retry:
            return []

        if previous_retry_count >= policy.max_payment_retries:
            return []

        product = self.merchant_data.get_product(
            failed_product_id
        )

        if product is None:
            return []

        revenue_at_risk = float(product["price"])

        return [
            RecoveryAction(
                action_id=(
                    f"RETRY-{failed_product_id}-"
                    f"{previous_retry_count + 1}"
                ),
                action_type="payment_retry",
                product_id=failed_product_id,
                revenue_at_risk=revenue_at_risk,
                recoverable_revenue=revenue_at_risk,
                customer_cost=0.0,
                merchant_value=(
                    revenue_at_risk
                    * float(product["margin_percent"])
                    / 100
                ),
                constraint_safe=True,
                success_probability=0.0,
                expected_recovery_value=0.0,
                reason=(
                    "Retry the failed payment because the merchant "
                    "policy permits payment retries and the retry limit "
                    "has not been reached."
                ),
            )
        ]

    def generate_offer_actions(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
        policy: MerchantPolicy,
    ) -> list[RecoveryAction]:

        product = self.merchant_data.get_product(
            failed_product_id
        )

        if product is None:
            return []

        revenue_at_risk = float(product["price"])
        margin_percent = float(product["margin_percent"])

        actions = []

        for offer in self.merchant_data.get_active_offers(
            failed_product_id
        ):

            if float(offer["min_order_value"]) > revenue_at_risk:
                continue

            discount_type = offer["discount_type"].lower()
            discount_value = float(offer["discount_value"])

            if discount_type == "percent":

                if discount_value > policy.max_discount_percent:
                    continue

                discount_amount = (
                    revenue_at_risk
                    * discount_value
                    / 100
                )

            elif discount_type == "flat":

                discount_amount = discount_value

                discount_percent = (
                    discount_amount
                    / revenue_at_risk
                    * 100
                )

                if discount_percent > policy.max_discount_percent:
                    continue

            else:
                continue

            if discount_amount > policy.max_incentive_amount:
                continue

            if margin_percent < policy.min_margin_percent:
                continue

            recoverable_revenue = max(
                revenue_at_risk - discount_amount,
                0.0,
            )

            remaining_margin = (
                recoverable_revenue
                * margin_percent
                / 100
            )

            actions.append(
                RecoveryAction(
                    action_id=f"OFFER-{offer['offer_id']}",
                    action_type="offer_incentive",
                    product_id=failed_product_id,
                    offer_id=offer["offer_id"],
                    revenue_at_risk=revenue_at_risk,
                    recoverable_revenue=recoverable_revenue,
                    customer_cost=discount_amount,
                    merchant_value=remaining_margin,
                    constraint_safe=True,
                    success_probability=0.0,
                    expected_recovery_value=0.0,
                    reason=(
                        f"Apply offer {offer['offer_id']} with an "
                        f"INR {discount_amount:.2f} incentive to recover "
                        f"the at-risk transaction within merchant "
                        f"policy limits."
                    ),
                )
            )

        return actions

    def generate_delivery_actions(
        self,
        intent: TransactionIntent,
        failed_product_id: str,
    ) -> list[RecoveryAction]:

        delivery = self.merchant_data.get_delivery_options(
            failed_product_id
        )

        product = self.merchant_data.get_product(
            failed_product_id
        )

        if delivery is None or product is None:
            return []

        express_available = (
            delivery["express_available"].lower()
            == "true"
        )

        if not express_available:
            return []

        standard_days = int(
            delivery["standard_days"]
        )

        express_days = int(
            delivery["express_days"]
        )

        if express_days >= standard_days:
            return []

        if intent.delivery_deadline_days is not None:
            if express_days > intent.delivery_deadline_days:
                return []

        revenue_at_risk = float(product["price"])

        return [
            RecoveryAction(
                action_id=(
                    f"DELIVERY-EXPRESS-{failed_product_id}"
                ),
                action_type="change_delivery",
                product_id=failed_product_id,
                revenue_at_risk=revenue_at_risk,
                recoverable_revenue=revenue_at_risk,
                customer_cost=0.0,
                merchant_value=0.0,
                constraint_safe=True,
                success_probability=0.0,
                expected_recovery_value=0.0,
                reason=(
                    f"Use express delivery for "
                    f"{failed_product_id} to reduce delivery "
                    f"time from {standard_days} day(s) to "
                    f"{express_days} day(s) while meeting "
                    f"the current delivery requirement."
                ),
            )
        ]
