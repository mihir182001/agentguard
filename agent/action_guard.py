
ALLOWED_ACTIONS = {
    "refund",
    "transfer",
    "status_change"
}

NON_EXECUTABLE_ACTIONS = {
    "investigate",
    "review",
    "manual_review",
    "inform_customer"
}


def check_action(
    action,
    customer_id,
    evidence,
    requires_human=True
):
    if action in NON_EXECUTABLE_ACTIONS:
        return {
            "allowed": True,
            "action_type": "non_executable",
            "reason": "No financial or transaction-changing action was requested."
        }

    if action not in ALLOWED_ACTIONS:
        return {
            "allowed": False,
            "action_type": "blocked",
            "reason": "Action is not supported."
        }

    if not customer_id:
        return {
            "allowed": False,
            "action_type": "blocked",
            "reason": "Customer identity is required."
        }

    if not evidence:
        return {
            "allowed": False,
            "action_type": "blocked",
            "reason": "Supporting evidence is required."
        }

    return {
        "allowed": False,
        "action_type": "human_approval",
        "reason": "Human approval is required before executing this action."
    }
