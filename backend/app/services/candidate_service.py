from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.candidate import ProductCandidate
from backend.app.services.merchant_data_service import MerchantDataService
from backend.app.services.constraint_service import ConstraintService


class CandidateService:

    def __init__(self):
        self.merchant_data = MerchantDataService()
        self.constraint_service = ConstraintService()

    def find_candidates(
        self,
        intent: TransactionIntent,
    ) -> list[ProductCandidate]:

        candidates = []

        products = self.merchant_data.get_all_products()

        for product in products:

            # Only consider products in the requested category
            if product["category"].lower() != intent.category.lower():
                continue

            inventory = self.merchant_data.get_inventory(
                product["product_id"]
            )

            delivery = self.merchant_data.get_delivery_options(
                product["product_id"]
            )

            result = self.constraint_service.evaluate_product(
                intent=intent,
                product=product,
                inventory=inventory,
                delivery=delivery,
            )

            available_quantity = (
                int(inventory["available_quantity"])
                if inventory
                else 0
            )

            if delivery:

                express_available = (
                    delivery["express_available"].lower()
                    == "true"
                )

                standard_days = int(
                    delivery["standard_days"]
                )

                express_days = int(
                    delivery["express_days"]
                )

                fastest_delivery = (
                    express_days
                    if express_available
                    else standard_days
                )

            else:
                fastest_delivery = -1

            candidates.append(
                ProductCandidate(
                    product_id=product["product_id"],
                    product_name=product["product_name"],
                    price=float(product["price"]),
                    rating=float(product["rating"]),
                    margin_percent=float(
                        product["margin_percent"]
                    ),
                    available_quantity=available_quantity,
                    fastest_delivery_days=fastest_delivery,
                    valid=result.valid,
                )
            )

        return candidates