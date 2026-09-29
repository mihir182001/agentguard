from agent.action_executor import execute_action


def test_action_blocked_without_approval():
    result = execute_action(
        {
            "allowed": True,
            "action": "refund"
        },
        approved=False
    )

    assert result["executed"] is False
    assert result["status"] == "blocked"


def test_action_executes_after_approval():
    result = execute_action(
        {
            "allowed": True,
            "action": "refund"
        },
        approved=True
    )

    assert result["executed"] is True
    assert result["status"] == "executed"


def test_guarded_action_cannot_execute():
    result = execute_action(
        {
            "allowed": False,
            "action": "refund"
        },
        approved=True
    )

    assert result["executed"] is False
    assert result["status"] == "blocked"


def test_unsupported_action_is_blocked():
    result = execute_action(
        {
            "allowed": True,
            "action": "delete_customer"
        },
        approved=True
    )

    assert result["executed"] is False
    assert result["status"] == "blocked"