from backend.app.models.transaction_intent import TransactionIntent
from backend.app.models.constraint_result import (
    ConstraintEvaluationResult,
    ConstraintViolation,
)


class ConstraintService:

    def evaluate_product(
        self,
        intent: TransactionIntent,
        product: dict,
        inventory: dict | None,
        delivery: dict | None,
    ) -> ConstraintEvaluationResult:

        violations = []

        # -------------------------
        # Inventory constraint
        # -------------------------
        if inventory is None:
            violations.append(
                ConstraintViolation(
                    constraint="inventory",
                    message="Inventory information is unavailable."
                )
            )

        else:
            available_quantity = int(
                inventory["available_quantity"]
            )

            if available_quantity < intent.quantity:
                violations.append(
                    ConstraintViolation(
                        constraint="inventory",
                        message="Product is not available in the requested quantity.",
                        required=str(intent.quantity),
                        available=str(available_quantity),
                    )
                )

        # -------------------------
        # Budget constraint
        # -------------------------
        if (
            intent.max_budget is not None
            and float(product["price"]) > intent.max_budget
        ):
            violations.append(
                ConstraintViolation(
                    constraint="max_budget",
                    message="Product price exceeds the customer's maximum budget.",
                    required=str(intent.max_budget),
                    available=str(product["price"]),
                )
            )

        # -------------------------
        # Rating constraint
        # -------------------------
        if (
            intent.min_rating is not None
            and float(product["rating"]) < intent.min_rating
        ):
            violations.append(
                ConstraintViolation(
                    constraint="min_rating",
                    message="Product rating is below the requested minimum.",
                    required=str(intent.min_rating),
                    available=str(product["rating"]),
                )
            )

        # -------------------------
        # Delivery constraint
        # -------------------------
        if (
            intent.delivery_deadline_days is not None
            and delivery is not None
        ):
            standard_days = int(delivery["standard_days"])

            express_available = (
                delivery["express_available"].lower() == "true"
            )

            express_days = int(delivery["express_days"])

            fastest_delivery = (
                express_days
                if express_available
                else standard_days
            )

            if fastest_delivery > intent.delivery_deadline_days:
                violations.append(
                    ConstraintViolation(
                        constraint="delivery_deadline",
                        message="Product cannot be delivered within the required deadline.",
                        required=str(
                            intent.delivery_deadline_days
                        ),
                        available=str(fastest_delivery),
                    )
                )

        # -------------------------
        # Final result
        # -------------------------
        return ConstraintEvaluationResult(
            valid=len(violations) == 0,
            violations=violations,
        )