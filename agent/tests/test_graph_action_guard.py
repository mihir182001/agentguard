from agent.graph import check_agent_action


def test_graph_blocks_unauthorized_refund():
    state = {
        "customer_id": "C000576",
        "evidence": {
            "transaction_id": "T0020008"
        },
        "decision": {
            "action": "refund",
            "requires_human": False
        }
    }

    result = check_agent_action(state)
    action = result["action_request"]

    assert action["allowed"] is False
    assert action["action_type"] == "human_approval"


def test_graph_allows_investigation():
    state = {
        "customer_id": "C000576",
        "evidence": {
            "transaction_id": "T0020008"
        },
        "decision": {
            "action": "investigate",
            "requires_human": False
        }
    }

    result = check_agent_action(state)
    action = result["action_request"]

    assert action["allowed"] is True
    assert action["action_type"] == "non_executable"