def execute_action(action_request, approved=False):
    if not approved:
        return {
            "executed": False,
            "status": "blocked",
            "reason": "Human approval is required."
        }

    if not action_request.get("allowed"):
        return {
            "executed": False,
            "status": "blocked",
            "reason": "Action was blocked by the Action Guard."
        }

    action_type = action_request.get("action")

    if action_type not in {"refund", "transfer", "status_change"}:
        return {
            "executed": False,
            "status": "blocked",
            "reason": "Unsupported action."
        }

    return {
        "executed": True,
        "status": "executed",
        "action": action_type
    }