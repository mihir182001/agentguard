from pathlib import Path
import sys
from typing import TypedDict
from agent.llm_decision import make_llm_decision
from agent.action_guard import check_action
from agent.tools.customer_tool import CustomerTool
from agent.tools.transaction_tool import TransactionTool
from agent.tools.policy_tool import PolicyTool

# Add the project root so the agent package can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.graph import StateGraph, START, END

from agent.llm_decision import make_llm_decision
from agent.tools.customer_tool import CustomerTool
from agent.tools.transaction_tool import TransactionTool
from agent.tools.policy_tool import PolicyTool


customer_tool = CustomerTool()
transaction_tool = TransactionTool()
policy_tool = PolicyTool()


class AgentState(TypedDict, total=False):
    case_id: str
    customer_id: str
    transaction_id: str
    issue_type: str
    description: str
    customer: dict
    transaction: dict
    related_transactions: list
    policies: list
    evidence: dict
    decision: dict
    action_request: dict


def get_customer(state: AgentState):
    customer = customer_tool.get_customer(
        state["customer_id"]
    )

    return {
        "customer": customer
    }


def get_transaction(state: AgentState):
    transaction = transaction_tool.get_transaction(
        state["transaction_id"]
    )

    return {
        "transaction": transaction
    }


def get_related_transactions(state: AgentState):
    related = transaction_tool.get_related_transactions(
        state["transaction_id"]
    )

    return {
        "related_transactions": related
    }


def get_policy(state: AgentState):
    query = (
        f"{state['issue_type']}. "
        f"{state['description']}"
    )

    policies = policy_tool.search_policy(
        query,
        top_k=3
    )

    return {
        "policies": policies
    }


def build_evidence(state: AgentState):
    evidence = {
        "customer": state["customer"],
        "transaction": state["transaction"],
        "related_transactions": state[
            "related_transactions"
        ],
        "policies": state["policies"],
    }

    return {
        "evidence": evidence
    }


def make_decision(state: AgentState):
    decision = make_llm_decision(
        case={
            "issue_type": state["issue_type"],
            "description": state["description"],
        },
        customer=state["customer"],
        transaction=state["transaction"],
        related_transactions=state[
            "related_transactions"
        ],
        policies=state["policies"],
    )

    return {
        "decision": decision.model_dump()
    }

def check_agent_action(state):
    decision = state["decision"]

    action = decision.get("action", "review")

    result = check_action(
        action=action,
        customer_id=state["customer_id"],
        evidence=state["evidence"]
    )

    return {"action_request": result}


def build_agent():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node(
        "get_customer",
        get_customer
    )

    workflow.add_node(
        "get_transaction",
        get_transaction
    )

    workflow.add_node(
        "get_related_transactions",
        get_related_transactions
    )

    workflow.add_node(
        "get_policy",
        get_policy
    )

    workflow.add_node(
        "build_evidence",
        build_evidence
    )

    workflow.add_node(
        "make_decision",
        make_decision
    )

    workflow.add_node("check_agent_action", check_agent_action)

    # Add edges
    workflow.add_edge(
        START,
        "get_customer"
    )

    workflow.add_edge(
        "get_customer",
        "get_transaction"
    )

    workflow.add_edge(
        "get_transaction",
        "get_related_transactions"
    )

    workflow.add_edge(
        "get_related_transactions",
        "get_policy"
    )

    workflow.add_edge(
        "get_policy",
        "build_evidence"
    )

    workflow.add_edge("build_evidence", "make_decision")
    workflow.add_edge("make_decision", "check_agent_action")
    workflow.add_edge("check_agent_action", END) 

    return workflow.compile()


# Compile the agent so other modules can import it
graph = build_agent()


if __name__ == "__main__":

    result = graph.invoke({
        "case_id": "TEST-001",
        "customer_id": "C000576",
        "transaction_id": "T0020008",
        "issue_type": "Duplicate Payment",
        "description": (
            "The customer believes they were "
            "charged twice for the same purchase."
        ),
    })

    print("\nAgentGuard Test")
    print("=" * 50)

    print("\nPrimary transaction:")
    print(result["transaction"])

    print("\nRelated transactions:")

    for transaction in result["related_transactions"]:
        print(
            f"{transaction['transaction_id']} - "
            f"{transaction['time_difference_seconds']:.1f} "
            f"seconds apart"
        )

    print("\nPolicies:")

    for policy in result["policies"]:
        print(
            f"{policy['source']} "
            f"(score={policy['final_score']:.3f})"
        )

    print("\nDecision:")
    print(result["decision"])