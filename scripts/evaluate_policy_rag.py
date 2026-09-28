from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.policy_retriever import PolicyRetriever


TEST_CASES = [
    {
        "query": "The customer was charged twice for the same payment.",
        "expected_policy": "duplicate_payment.md",
    },
    {
        "query": "The customer wants a refund for a transaction.",
        "expected_policy": "refund_policy.md",
    },
    {
        "query": "The payment failed but the customer later tried again and it succeeded.",
        "expected_policy": "failed_payment.md",
    },
    {
        "query": "A transaction looks suspicious and may indicate fraud.",
        "expected_policy": "fraud_policy.md",
    },
    {
        "query": "The customer made an unusually large transaction.",
        "expected_policy": "large_transaction.md",
    },
    {
        "query": "Several transactions happened within a few seconds.",
        "expected_policy": "rapid_transaction.md",
    },
    {
        "query": "The customer made a transaction in another country.",
        "expected_policy": "international_transaction.md",
    },
    {
        "query": "The customer is reporting an issue with a cash withdrawal.",
        "expected_policy": "cash_withdrawal.md",
    },
    {
        "query": "The customer has a problem with a bank transfer.",
        "expected_policy": "bank_transfer.md",
    },
    {
        "query": "The customer wants to replace their card.",
        "expected_policy": "card_replacement.md",
    },
]


def calculate_mrr(results, expected_policy):
    """Calculate reciprocal rank for the expected policy."""

    for rank, result in enumerate(results, start=1):
        if result["source"] == expected_policy:
            return 1 / rank

    return 0.0


def main():
    retriever = PolicyRetriever()

    # Load the existing policy chunks and build the same baseline index.
    retriever.load_policies()
    retriever.build_index()

    top_1_correct = 0
    top_3_correct = 0
    reciprocal_ranks = []

    print("\nPolicy RAG Evaluation")
    print("=" * 80)

    for test_case in TEST_CASES:
        query = test_case["query"]
        expected_policy = test_case["expected_policy"]

        results = retriever.search(query, top_k=3)

        retrieved_policies = [
            result["source"]
            for result in results
        ]

        top_1_match = (
            retrieved_policies[0] == expected_policy
        )

        top_3_match = (
            expected_policy in retrieved_policies
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

        print(f"\nQuery: {query}")
        print(f"Expected: {expected_policy}")
        print(f"Retrieved: {retrieved_policies}")
        print(f"Reciprocal rank: {reciprocal_rank:.3f}")

    total_cases = len(TEST_CASES)

    top_1_accuracy = top_1_correct / total_cases
    top_3_accuracy = top_3_correct / total_cases
    mrr = sum(reciprocal_ranks) / total_cases

    print("\n" + "=" * 80)
    print("Evaluation Results")
    print("=" * 80)

    print(
        f"Top-1 Accuracy: {top_1_accuracy:.2%}"
    )
    print(
        f"Top-3 Accuracy: {top_3_accuracy:.2%}"
    )
    print(
        f"MRR:            {mrr:.3f}"
    )


if __name__ == "__main__":
    main()