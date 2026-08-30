from backend.app.models.execution_request import ExecutionRequest
from backend.app.models.execution_result import ExecutionResult


class ExecutionService:

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

        return ExecutionResult(
            executed=True,
            status="EXECUTED",
            reason="Execution gate conditions satisfied.",
            action_id=request.action_id,
        )