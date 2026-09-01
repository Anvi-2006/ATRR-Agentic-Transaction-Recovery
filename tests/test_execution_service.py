from backend.app.models.execution_request import ExecutionRequest
from backend.app.services.execution_service import ExecutionService


def test_execution_requires_policy_approval():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="SUB-P001",
        policy_approved=False,
        customer_approved=True,
    )

    result = service.execute(request)

    assert result.executed is False
    assert result.status == "BLOCKED"


def test_execution_requires_customer_approval():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="SUB-P001",
        policy_approved=True,
        customer_approved=False,
    )

    result = service.execute(request)

    assert result.executed is False
    assert result.status == "BLOCKED"


def test_execution_requires_both_approvals():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="SUB-P001",
        policy_approved=False,
        customer_approved=False,
    )

    result = service.execute(request)

    assert result.executed is False
    assert result.status == "BLOCKED"


def test_execution_succeeds_when_gate_conditions_pass():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="SUB-P001",
        policy_approved=True,
        customer_approved=True,
    )

    result = service.execute(request)

    assert result.executed is True
    assert result.status == "EXECUTED"


def test_execution_result_contains_reason():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="SUB-P001",
        policy_approved=True,
        customer_approved=True,
    )

    result = service.execute(request)

    assert result.reason
def test_simulation_can_fail_first_payment_retry():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="RETRY-P003-1",
        policy_approved=True,
        customer_approved=True,
        simulation_mode=True,
        attempt_number=1,
    )

    result = service.execute(request)

    assert result.executed is False
    assert result.status == "FAILED"


def test_simulation_can_succeed_after_failure():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="RETRY-P003-1",
        policy_approved=True,
        customer_approved=True,
        simulation_mode=True,
        attempt_number=2,
    )

    result = service.execute(request)

    assert result.executed is True
    assert result.status == "EXECUTED"


def test_normal_execution_mode_still_succeeds():

    service = ExecutionService()

    request = ExecutionRequest(
        action_id="RETRY-P003-1",
        policy_approved=True,
        customer_approved=True,
    )

    result = service.execute(request)

    assert result.executed is True
    assert result.status == "EXECUTED"
