from agent.action_guard import check_action
from agent.action_executor import execute_action


def test_allowed_action_without_approval_is_blocked():
    guard_result = check_action(
        action="refund",
        customer_id="C000576",
        evidence={
            "transaction_id": "T0020008"
        }
    )

    execution_result = execute_action(
        {
            "allowed": guard_result["allowed"],
            "action": "refund"
        },
        approved=False
    )

    assert guard_result["allowed"] is False
    assert execution_result["executed"] is False


def test_blocked_action_cannot_execute_with_approval():
    execution_result = execute_action(
        {
            "allowed": False,
            "action": "refund"
        },
        approved=True
    )

    assert execution_result["executed"] is False


def test_unsupported_action_cannot_execute():
    guard_result = check_action(
        action="delete_customer",
        customer_id="C000576",
        evidence={
            "transaction_id": "T0020008"
        }
    )

    execution_result = execute_action(
        {
            "allowed": guard_result["allowed"],
            "action": "delete_customer"
        },
        approved=True
    )

    assert guard_result["allowed"] is False
    assert execution_result["executed"] is False


def test_approved_guarded_action_can_execute():
    execution_result = execute_action(
        {
            "allowed": True,
            "action": "refund"
        },
        approved=True
    )

    assert execution_result["executed"] is True
    assert execution_result["status"] == "executed"