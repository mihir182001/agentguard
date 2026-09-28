from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.policy_retriever import PolicyRetriever


SUPPORT_CASE_FILE = "data/raw/support_cases.csv"
SCENARIO_FILE = "data/processed/scenario_labels.csv"


ISSUE_TO_POLICY = {
    "Duplicate Payment": "duplicate_payment.md",
    "Refund Request": "refund_policy.md",
    "Failed Payment": "failed_payment.md",
    "Suspicious Transaction": "fraud_policy.md",
    "Large Transaction": "large_transaction.md",
    "Rapid Transactions": "rapid_transaction.md",
    "International Transaction": "international_transaction.md",
    "Cash Withdrawal": "cash_withdrawal.md",
    "Bank Transfer": "bank_transfer.md",
    "Card Replacement": "card_replacement.md",
}


def load_evaluation_cases():
    """Load support cases and assign the expected policy."""

    support_cases = pd.read_csv(SUPPORT_CASE_FILE)

    support_cases["expected_policy"] = (
        support_cases["issue_type"]
        .map(ISSUE_TO_POLICY)
    )

    # Ignore issue types that do not yet have a policy.
    evaluation_cases = support_cases.dropna(
        subset=["expected_policy"]
    ).copy()

    return evaluation_cases


def calculate_mrr(results, expected_policy):
    """Calculate reciprocal rank for the expected policy."""

    # Only count the first occurrence of each policy.
    seen_policies = set()
    unique_results = []

    for result in results:
        policy = result["source"]

        if policy not in seen_policies:
            seen_policies.add(policy)
            unique_results.append(result)

    for rank, result in enumerate(unique_results, start=1):
        if result["source"] == expected_policy:
            return 1 / rank

    return 0.0


def main():
    print("Loading evaluation dataset...")

    cases = load_evaluation_cases()

    print(f"Evaluation cases: {len(cases):,}")

    retriever = PolicyRetriever()
    retriever.load_policies()
    retriever.build_index()

    top_1_correct = 0
    top_3_correct = 0
    reciprocal_ranks = []

    print("\nRunning realistic RAG evaluation...")
    print("=" * 80)

    for _, case in cases.iterrows():
        query = case["description"]
        expected_policy = case["expected_policy"]

        results = retriever.search(
            query,
            top_k=10,
        )

        # Remove duplicate policy files from the results.
        retrieved_policies = []
        seen_policies = set()

        for result in results:
            policy = result["source"]

            if policy not in seen_policies:
                seen_policies.add(policy)
                retrieved_policies.append(policy)

        top_1_match = (
            len(retrieved_policies) > 0
            and retrieved_policies[0] == expected_policy
        )

        top_3_match = (
            expected_policy in retrieved_policies[:3]
        )

        reciprocal_rank = calculate_mrr(
            results,
            expected_policy,
        )

        if top_1_match:
            top_1_correct += 1

        if top_3_match:
            top_3_correct += 1

        reciprocal_ranks.append(reciprocal_rank)

    total_cases = len(cases)

    top_1_accuracy = top_1_correct / total_cases
    top_3_accuracy = top_3_correct / total_cases
    mrr = sum(reciprocal_ranks) / total_cases

    print("\n" + "=" * 80)
    print("REALISTIC POLICY RAG RESULTS")
    print("=" * 80)

    print(f"Total cases:    {total_cases:,}")
    print(f"Top-1 Accuracy: {top_1_accuracy:.2%}")
    print(f"Top-3 Accuracy: {top_3_accuracy:.2%}")
    print(f"MRR:            {mrr:.3f}")


if __name__ == "__main__":
    main()