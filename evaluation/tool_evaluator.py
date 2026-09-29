from pathlib import Path
import sys
import pandas as pd


# Add the project root so Python can import the agent package.
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from agent.graph import graph
from evaluation.test_cases import load_test_cases


# Folder for saving evaluation results.
RESULTS_DIR = ROOT / "evaluation" / "results"
RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Define which tools/evidence are required
# for each scenario.
TOOL_REQUIREMENTS = {

    "unusual_location": {
        "customer": True,
        "transaction": True,
        "related_transactions": False,
        "policies": True
    },

    "duplicate_payment": {
        "customer": True,
        "transaction": True,
        "related_transactions": True,
        "policies": True
    },

    "large_transaction": {
        "customer": True,
        "transaction": True,
        "related_transactions": False,
        "policies": True
    },

    "rapid_transactions": {
        "customer": True,
        "transaction": True,
        "related_transactions": True,
        "policies": True
    },

    "failed_successful_retry": {
        "customer": True,
        "transaction": True,
        "related_transactions": True,
        "policies": True
    }
}


def check_customer_tool(result):
    """Check whether customer information was retrieved."""

    customer = result.get(
        "customer"
    )

    if not customer:
        return False

    return bool(
        customer.get("found", False)
    )


def check_transaction_tool(result):
    """Check whether the primary transaction was retrieved."""

    transaction = result.get(
        "transaction"
    )

    if not transaction:
        return False

    return bool(
        transaction.get("found", False)
    )


def check_related_transactions(result):
    """
    Check whether related transaction evidence
    was retrieved when required.
    """

    related = result.get(
        "related_transactions"
    )

    if related is None:
        return False

    return len(related) > 0


def check_policy_tool(result):
    """Check whether policy evidence was retrieved."""

    policies = result.get(
        "policies"
    )

    if not policies:
        return False

    return len(policies) > 0


def evaluate_tool_usage(case, result):
    """
    Compare the tools/evidence retrieved by the agent
    against the requirements for the scenario.
    """

    scenario = case["scenario"]

    if scenario not in TOOL_REQUIREMENTS:

        raise ValueError(
            f"No tool requirements defined for "
            f"scenario: {scenario}"
        )

    requirements = TOOL_REQUIREMENTS[
        scenario
    ]

    customer_used = check_customer_tool(
        result
    )

    transaction_used = check_transaction_tool(
        result
    )

    related_used = check_related_transactions(
        result
    )

    policy_used = check_policy_tool(
        result
    )

    customer_pass = (
        not requirements["customer"]
        or customer_used
    )

    transaction_pass = (
        not requirements["transaction"]
        or transaction_used
    )

    related_pass = (
        not requirements["related_transactions"]
        or related_used
    )

    policy_pass = (
        not requirements["policies"]
        or policy_used
    )

    tool_use_pass = all([
        customer_pass,
        transaction_pass,
        related_pass,
        policy_pass
    ])

    return {
        "customer_used": customer_used,
        "transaction_used": transaction_used,
        "related_transactions_used": related_used,
        "policy_used": policy_used,

        "customer_pass": customer_pass,
        "transaction_pass": transaction_pass,
        "related_transactions_pass": related_pass,
        "policy_pass": policy_pass,

        "tool_use_pass": tool_use_pass
    }


def evaluate_case(case):
    """Run one case through the AgentGuard graph."""

    initial_state = {

        "case_id": case["case_id"],

        "customer_id": case["customer_id"],

        "transaction_id": case["transaction_id"],

        "issue_type": case["issue_type"],

        "description": case["description"]
    }

    result = graph.invoke(
        initial_state
    )

    tool_results = evaluate_tool_usage(
        case,
        result
    )

    return {

        "case_id":
            case["case_id"],

        "scenario":
            case["scenario"],

        "transaction_id":
            case["transaction_id"],

        "customer_used":
            tool_results["customer_used"],

        "transaction_used":
            tool_results["transaction_used"],

        "related_transactions_used":
            tool_results[
                "related_transactions_used"
            ],

        "policy_used":
            tool_results["policy_used"],

        "tool_use_pass":
            tool_results["tool_use_pass"]
    }


def print_summary(results):
    """Print the tool-use evaluation summary."""

    df = pd.DataFrame(
        results
    )

    print()
    print("=" * 70)
    print("AgentGuard Tool-Use Evaluation")
    print("=" * 70)

    print()

    print(
        f"Customer tool usage       "
        f"{df['customer_used'].mean() * 100:.1f}%"
    )

    print(
        f"Transaction tool usage    "
        f"{df['transaction_used'].mean() * 100:.1f}%"
    )

    print(
        f"Related transaction usage "
        f"{df['related_transactions_used'].mean() * 100:.1f}%"
    )

    print(
        f"Policy tool usage         "
        f"{df['policy_used'].mean() * 100:.1f}%"
    )

    print()

    print(
        f"Overall tool-use accuracy "
        f"{df['tool_use_pass'].mean() * 100:.1f}%"
    )

    print()

    print("Case results")
    print("-" * 70)

    columns = [

        "case_id",

        "scenario",

        "customer_used",

        "transaction_used",

        "related_transactions_used",

        "policy_used",

        "tool_use_pass"
    ]

    print(
        df[columns].to_string(
            index=False
        )
    )

    return df


def main():
    """Run the complete tool-use evaluation."""

    print(
        "Loading AgentGuard evaluation cases..."
    )

    cases = load_test_cases()

    print(
        f"Loaded {len(cases)} test cases."
    )

    results = []

    for case in cases:

        print()

        print(
            f"Running {case['case_id']} "
            f"({case['scenario']})..."
        )

        result = evaluate_case(
            case
        )

        results.append(
            result
        )

        print(
            f"Customer tool: "
            f"{result['customer_used']}"
        )

        print(
            f"Transaction tool: "
            f"{result['transaction_used']}"
        )

        print(
            f"Related transactions: "
            f"{result['related_transactions_used']}"
        )

        print(
            f"Policy tool: "
            f"{result['policy_used']}"
        )

        print(
            f"Tool-use pass: "
            f"{result['tool_use_pass']}"
        )

    df = print_summary(
        results
    )

    output_file = (
        RESULTS_DIR
        / "tool_use_results.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()

    print(
        "Results saved to:"
    )

    print(
        output_file
    )


if __name__ == "__main__":

    main()