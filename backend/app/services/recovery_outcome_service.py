from backend.app.models.recovery_action import RecoveryAction
from backend.app.models.recovery_attempt import RecoveryAttempt
from backend.app.models.recovery_outcome import RecoveryOutcome


class RecoveryOutcomeService:

    BASE_PROBABILITIES = {
        "payment_retry": 0.55,
        "substitute_product": 0.70,
        "offer_incentive": 0.65,
        "change_delivery": 0.60,
    }

    def estimate(
        self,
        action: RecoveryAction,
        previous_attempts: list[RecoveryAttempt] | None = None,
    ) -> RecoveryOutcome:

        previous_attempts = previous_attempts or []

        probability = self.BASE_PROBABILITIES.get(
            action.action_type,
            0.50,
        )

        factors = {}
        explanations = []

        # -----------------------------------------
        # Constraint safety
        # -----------------------------------------

        if action.constraint_safe:
            probability += 0.05
            factors["constraint_fit"] = 0.05
            explanations.append("customer constraints are satisfied")
        else:
            probability -= 0.25
            factors["constraint_fit"] = -0.25
            explanations.append("constraint mismatch reduces success likelihood")

        # -----------------------------------------
        # Policy safety
        # -----------------------------------------

        if action.action_type != "payment_retry":
            factors["policy_context"] = 0.0

        # -----------------------------------------
        # Previous failed attempts
        # -----------------------------------------

        same_action_failures = sum(
            1
            for attempt in previous_attempts
            if attempt.action_id == action.action_id
            and attempt.status.upper() == "FAILED"
        )

        if same_action_failures:
            penalty = min(
                same_action_failures * 0.15,
                0.30,
            )

            probability -= penalty
            factors["previous_failure"] = -penalty
            explanations.append(
                f"{same_action_failures} previous failure(s) reduce confidence"
            )
        else:
            factors["previous_failure"] = 0.0

        # -----------------------------------------
        # Action-specific factors
        # -----------------------------------------

        if action.action_type == "payment_retry":
            retry_attempts = sum(
                1
                for attempt in previous_attempts
                if attempt.action_id.startswith("RETRY-")
            )

            if retry_attempts == 0:
                factors["first_retry"] = 0.05
                probability += 0.05
                explanations.append(
                    "first retry has no prior retry failure"
                )

            else:
                retry_penalty = min(
                    retry_attempts * 0.12,
                    0.24,
                )

                factors["retry_history"] = -retry_penalty
                probability -= retry_penalty
                explanations.append(
                    f"{retry_attempts} previous retry attempt(s) "
                    "reduce retry effectiveness"
                )

        elif action.action_type == "substitute_product":
            if action.product_id:
                factors["alternative_product"] = 0.05
                probability += 0.05
                explanations.append(
                    "a valid alternative product is available"
                )

        elif action.action_type == "offer_incentive":
            if action.customer_cost == 0:
                factors["incentive_cost"] = 0.0

            elif action.customer_cost <= 200:
                factors["small_incentive"] = 0.05
                probability += 0.05
                explanations.append(
                    "small incentive may improve recovery likelihood"
                )

            else:
                factors["large_incentive"] = -0.05
                probability -= 0.05
                explanations.append(
                    "larger incentive reduces expected efficiency"
                )

        elif action.action_type == "change_delivery":
            factors["delivery_option"] = 0.05
            probability += 0.05
            explanations.append(
                "delivery alternative is available"
            )

        probability = min(
            max(probability, 0.05),
            0.95,
        )

        confidence = min(
            0.95,
            0.65 + (
                len(factors) * 0.05
            ),
        )

        explanation = (
            f"Estimated success probability is "
            f"{probability:.2f} because "
            + ", ".join(explanations)
            + "."
        )

        return RecoveryOutcome(
            intervention_id=action.action_id,
            success_probability=round(probability, 2),
            confidence=round(confidence, 2),
            factors=factors,
            explanation=explanation,
        )

    def estimate_batch(
        self,
        actions: list[RecoveryAction],
        previous_attempts: list[RecoveryAttempt] | None = None,
    ) -> list[RecoveryOutcome]:

        return [
            self.estimate(
                action=action,
                previous_attempts=previous_attempts,
            )
            for action in actions
        ]
