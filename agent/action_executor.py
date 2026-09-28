def execute_action(action_request, approved=False):

    action_type = action_request.get("action")
    action_guard_type = action_request.get("action_type")

    non_executable_actions = {
        "investigate",
        "review",
        "manual_review",
        "inform_customer"
    }

    if action_type in non_executable_actions:
        return {
            "executed": False,
            "status": "not_required",
            "reason": "No executable action was requested."
        }

    if action_guard_type == "blocked":
        return {
            "executed": False,
            "status": "blocked",
            "reason": "Action was blocked by the Action Guard."
        }

    if action_guard_type == "human_approval" and not approved:
        return {
            "executed": False,
            "status": "pending_human_approval",
            "reason": "Human approval is required."
        }

    if not approved:
        return {
            "executed": False,
            "status": "pending_human_approval",
            "reason": "Human approval is required."
        }

    if action_type not in {
        "refund",
        "transfer",
        "status_change"
    }:
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