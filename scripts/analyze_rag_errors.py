from pathlib import Path
import sys

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from rag.policy_retriever import PolicyRetriever


SUPPORT_CASE_FILE = "data/raw/support_cases.csv"
ERROR_FILE = "data/processed/rag_errors.csv"


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


def load_cases():
    """Load support cases and assign the expected policy."""

    cases = pd.read_csv(SUPPORT_CASE_FILE)

    cases["expected_policy"] = (
        cases["issue_type"]
        .map(ISSUE_TO_POLICY)
    )

    return cases.dropna(
        subset=["expected_policy"]
    ).copy()


def main():
    print("Loading support cases...")

    cases = load_cases()

    print(f"Evaluation cases: {len(cases):,}")

    retriever = PolicyRetriever()
    retriever.load_policies()
    retriever.build_index()

    errors = []

    print("\nAnalyzing retrieval errors...")

    for _, case in cases.iterrows():
        results = retriever.search(
            case["description"],
            top_k=10,
        )

        if not results:
            continue

        top_result = results[0]

        expected_policy = case["expected_policy"]
        predicted_policy = top_result["source"]

        if predicted_policy != expected_policy:
            errors.append(
                {
                    "case_id": case["case_id"],
                    "issue_type": case["issue_type"],
                    "description": case["description"],
                    "expected_policy": expected_policy,
                    "predicted_policy": predicted_policy,
                    "retrieval_score": round(
                        top_result["score"],
                        4,
                    ),
                }
            )

    error_df = pd.DataFrame(errors)

    Path("data/processed").mkdir(
        parents=True,
        exist_ok=True,
    )

    error_df.to_csv(
        ERROR_FILE,
        index=False,
    )

    print("\n" + "=" * 80)
    print("RAG ERROR ANALYSIS")
    print("=" * 80)

    print(f"Total errors: {len(error_df):,}")

    if error_df.empty:
        print("No retrieval errors found.")
        return

    print("\nErrors by issue type:")
    print(
        error_df["issue_type"]
        .value_counts()
        .to_string()
    )

    print("\nMost common incorrect predictions:")

    prediction_counts = (
        error_df[
            [
                "expected_policy",
                "predicted_policy",
            ]
        ]
        .value_counts()
        .head(15)
    )

    print(prediction_counts.to_string())

    print("\nExample errors:")
    print("-" * 80)

    for _, error in error_df.head(10).iterrows():
        print(f"\nCase: {error['case_id']}")
        print(f"Issue: {error['issue_type']}")
        print(f"Description: {error['description']}")
        print(f"Expected: {error['expected_policy']}")
        print(f"Predicted: {error['predicted_policy']}")
        print(f"Score: {error['retrieval_score']}")

    print("\nSaved errors to:")
    print(ERROR_FILE)


if __name__ == "__main__":
    main()