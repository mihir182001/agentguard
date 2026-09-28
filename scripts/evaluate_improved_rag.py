"""
Evaluate the improved hybrid policy retriever.

This benchmark compares the improved retriever against the
frozen baseline benchmark.

Metrics:
- Top-1 Accuracy
- Top-3 Accuracy
- Mean Reciprocal Rank (MRR)
"""

from pathlib import Path
import sys

import pandas as pd


# Allow imports from the project root.
sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from rag.improved_retriever import ImprovedPolicyRetriever


DATA_PATH = Path(
    "data/raw/support_cases.csv"
)


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


def reciprocal_rank(results, expected_policy):
    """
    Calculate reciprocal rank for one query.

    Examples:
        Rank 1 -> 1.0
        Rank 2 -> 0.5
        Rank 3 -> 0.333
        Not found -> 0.0
    """

    for rank, result in enumerate(results, start=1):

        if result["source"] == expected_policy:
            return 1.0 / rank

    return 0.0


def main():

    print("\nImproved Policy RAG Evaluation")
    print("=" * 75)

    # ---------------------------------------------------------
    # Load support cases
    # ---------------------------------------------------------

    cases = pd.read_csv(DATA_PATH)

    # Keep only cases with a known policy mapping.
    cases = cases[
        cases["issue_type"].isin(ISSUE_TO_POLICY)
    ].copy()

    print(
        f"Evaluation cases: {len(cases):,}"
    )

    # ---------------------------------------------------------
    # Create retriever
    # ---------------------------------------------------------

    retriever = ImprovedPolicyRetriever()

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    top1_correct = 0
    top3_correct = 0

    reciprocal_ranks = []

    errors = []

    total = len(cases)

    for processed, (_, row) in enumerate(
        cases.iterrows(),
        start=1
    ):

        query = row["description"]

        expected_policy = ISSUE_TO_POLICY[
            row["issue_type"]
        ]

        results = retriever.search(
            query,
            top_k=3
        )

        ranked_policies = [
            result["source"]
            for result in results
        ]

        # -----------------------------------------------------
        # Top-1 accuracy
        # -----------------------------------------------------

        if (
            len(ranked_policies) >= 1
            and ranked_policies[0] == expected_policy
        ):
            top1_correct += 1

        # -----------------------------------------------------
        # Top-3 accuracy
        # -----------------------------------------------------

        if expected_policy in ranked_policies:
            top3_correct += 1

        # -----------------------------------------------------
        # Mean Reciprocal Rank
        # -----------------------------------------------------

        rr = reciprocal_rank(
            results,
            expected_policy
        )

        reciprocal_ranks.append(rr)

        # -----------------------------------------------------
        # Save incorrect predictions
        # -----------------------------------------------------

        if (
            not ranked_policies
            or ranked_policies[0] != expected_policy
        ):
            errors.append(
                {
                    "case_id": row["case_id"],
                    "issue_type": row["issue_type"],
                    "description": query,
                    "expected_policy": expected_policy,
                    "predicted_policy": (
                        ranked_policies[0]
                        if ranked_policies
                        else None
                    ),
                    "ranked_policies": ranked_policies,
                    "top_score": (
                        results[0]["final_score"]
                        if results
                        else None
                    ),
                }
            )

        # -----------------------------------------------------
        # Progress
        # -----------------------------------------------------

        if (
            processed % 500 == 0
            or processed == total
        ):
            print(
                f"Processed {processed:,}/{total:,}"
            )

    # ---------------------------------------------------------
    # Calculate metrics
    # ---------------------------------------------------------

    top1_accuracy = (
        top1_correct / total
        if total
        else 0.0
    )

    top3_accuracy = (
        top3_correct / total
        if total
        else 0.0
    )

    mrr = (
        sum(reciprocal_ranks) / total
        if total
        else 0.0
    )

    # ---------------------------------------------------------
    # Print results
    # ---------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("IMPROVED RAG RESULTS")
    print("=" * 75)

    print(
        f"Total cases:    {total:,}"
    )

    print(
        f"Top-1 Accuracy: {top1_accuracy:.2%}"
    )

    print(
        f"Top-3 Accuracy: {top3_accuracy:.2%}"
    )

    print(
        f"MRR:            {mrr:.3f}"
    )

    print(
        f"Top-1 errors:   {len(errors):,}"
    )

    print("=" * 75)

    # ---------------------------------------------------------
    # Compare against frozen baseline
    # ---------------------------------------------------------

    baseline_top1 = 0.9273
    baseline_top3 = 0.9987
    baseline_mrr = 0.962

    print("\nComparison with frozen baseline")
    print("-" * 75)

    print(
        f"Top-1: "
        f"{baseline_top1:.2%} -> "
        f"{top1_accuracy:.2%} "
        f"({top1_accuracy - baseline_top1:+.2%})"
    )

    print(
        f"Top-3: "
        f"{baseline_top3:.2%} -> "
        f"{top3_accuracy:.2%} "
        f"({top3_accuracy - baseline_top3:+.2%})"
    )

    print(
        f"MRR:   "
        f"{baseline_mrr:.3f} -> "
        f"{mrr:.3f} "
        f"({mrr - baseline_mrr:+.3f})"
    )

    # ---------------------------------------------------------
    # Save errors
    # ---------------------------------------------------------

    error_path = Path(
        "data/processed/improved_rag_errors.csv"
    )

    error_df = pd.DataFrame(errors)

    error_df.to_csv(
        error_path,
        index=False
    )

    print(
        f"\nSaved errors to: {error_path}"
    )


if __name__ == "__main__":
    main()