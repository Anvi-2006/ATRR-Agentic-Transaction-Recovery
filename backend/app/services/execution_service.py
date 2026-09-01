from backend.app.models.execution_request import ExecutionRequest
from backend.app.models.execution_result import ExecutionResult


class ExecutionService:

    SIMULATED_FAILURE_RULES = {
        "payment_retry": {1},
        "offer_incentive": {2},
        "change_delivery": {1},
    }

    def execute(
        self,
        request: ExecutionRequest,
    ) -> ExecutionResult:

        if not request.policy_approved:

            return ExecutionResult(
                executed=False,
                status="BLOCKED",
                reason="Policy approval is required before execution.",
                action_id=request.action_id,
            )

        if not request.customer_approved:

            return ExecutionResult(
                executed=False,
                status="BLOCKED",
                reason="Customer approval is required before execution.",
                action_id=request.action_id,
            )

        # -----------------------------------------
        # Normal execution mode
        # -----------------------------------------

        if not request.simulation_mode:

            return ExecutionResult(
                executed=True,
                status="EXECUTED",
                reason="Execution gate conditions satisfied.",
                action_id=request.action_id,
            )

        # -----------------------------------------
        # Scenario-driven simulation
        # -----------------------------------------

        scenario = request.simulation_scenario

        if scenario == "STOP":

            return ExecutionResult(
                executed=False,
                status="BLOCKED",
                reason=(
                    "Simulation stop scenario prevented execution."
                ),
                action_id=request.action_id,
            )

        if scenario == "ESCALATE":

            return ExecutionResult(
                executed=False,
                status="FAILED",
                reason=(
                    "Simulated execution failure under the "
                    "escalation scenario."
                ),
                action_id=request.action_id,
            )

        # -----------------------------------------
        # REPLAN scenario
        # -----------------------------------------

        if scenario == "REPLAN":

            if request.attempt_number == 1:

                return ExecutionResult(
                    executed=False,
                    status="FAILED",
                    reason=(
                        "Simulated first-attempt failure to trigger "
                        "adaptive replanning."
                    ),
                    action_id=request.action_id,
                )

            return ExecutionResult(
                executed=True,
                status="EXECUTED",
                reason=(
                    "Simulated recovery succeeded after replanning."
                ),
                action_id=request.action_id,
            )

        # -----------------------------------------
        # NORMAL simulation
        # -----------------------------------------

        action_type = self._get_action_type(
            request.action_id
        )

        failure_attempts = self.SIMULATED_FAILURE_RULES.get(
            action_type,
            set(),
        )

        if request.attempt_number in failure_attempts:

            return ExecutionResult(
                executed=False,
                status="FAILED",
                reason=(
                    f"Simulated {action_type} execution failure "
                    f"on attempt {request.attempt_number}."
                ),
                action_id=request.action_id,
            )

        return ExecutionResult(
            executed=True,
            status="EXECUTED",
            reason=(
                f"Simulated {action_type} execution succeeded "
                f"on attempt {request.attempt_number}."
            ),
            action_id=request.action_id,
        )

    @staticmethod
    def _get_action_type(action_id: str) -> str:

        if action_id.startswith("RETRY-"):
            return "payment_retry"

        if action_id.startswith("OFFER-"):
            return "offer_incentive"

        if action_id.startswith("DELIVERY-"):
            return "change_delivery"

        if action_id.startswith("SUB-"):
            return "substitute_product"

        return "unknown"
