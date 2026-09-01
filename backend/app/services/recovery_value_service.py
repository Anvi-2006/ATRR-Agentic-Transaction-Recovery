from backend.app.models.recovery_intervention import RecoveryIntervention


class RecoveryValueService:

    def calculate(
        self,
        intervention: RecoveryIntervention,
    ) -> float:

        expected_revenue = (
            intervention.recoverable_revenue
            * intervention.success_probability
        )

        net_recovery_value = (
            expected_revenue
            - intervention.merchant_cost
        )

        return max(net_recovery_value, 0.0)

    def score(
        self,
        interventions: list[RecoveryIntervention],
    ) -> list[RecoveryIntervention]:

        scored = []

        for intervention in interventions:

            intervention.expected_recovery_value = (
                self.calculate(intervention)
            )

            scored.append(intervention)

        return sorted(
            scored,
            key=lambda item: item.expected_recovery_value,
            reverse=True,
        )
