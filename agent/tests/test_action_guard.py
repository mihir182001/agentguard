from agent.action_guard import check_action


def test_refund_requires_human():
    result = check_action(
        action="refund",
        customer_id="C000576",
        evidence={
            "transaction_id": "T0020008",
            "policy": "refund_policy"
        },
        requires_human=True
    )

    assert result["allowed"] is False


def test_unknown_action_is_blocked():
    result = check_action(
        action="delete_customer",
        customer_id="C000576",
        evidence={
            "transaction_id": "T0020008"
        },
        requires_human=False
    )

    assert result["allowed"] is False


def test_missing_customer_is_blocked():
    result = check_action(
        action="refund",
        customer_id=None,
        evidence={
            "transaction_id": "T0020008"
        },
        requires_human=False
    )

    assert result["allowed"] is False

def test_executable_action_always_requires_human():
    result = check_action(
        action="refund",
        customer_id="C000576",
        evidence={
            "transaction_id": "T0020008"
        },
        requires_human=False
    )

    assert result["allowed"] is False
    assert result["action_type"] == "human_approval"