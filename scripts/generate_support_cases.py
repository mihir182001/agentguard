import os
import random

import pandas as pd
from faker import Faker


# Reproducible results
SEED = 42
random.seed(SEED)
Faker.seed(SEED)

fake = Faker()


# Input/output files
CUSTOMERS_PATH = "data/raw/customers.csv"
TRANSACTIONS_PATH = "data/raw/transactions_with_scenarios.csv"
SCENARIO_LABELS_PATH = "data/processed/scenario_labels.csv"
OUTPUT_PATH = "data/raw/support_cases.csv"

NUM_CASES = 5000


# Support issue types
ISSUE_TYPES = [
    "Duplicate Payment",
    "Refund Request",
    "Suspicious Transaction",
    "Failed Payment",
    "Large Transaction",
    "International Transaction",
    "Bank Transfer",
    "Cash Withdrawal",
    "Rapid Transactions",
    "General Transaction",
    "Card Replacement",
    "Account Access",
]


# Approximate distribution of support cases
ISSUE_WEIGHTS = [
    0.15,  # Duplicate Payment
    0.12,  # Refund Request
    0.10,  # Suspicious Transaction
    0.10,  # Failed Payment
    0.08,  # Large Transaction
    0.08,  # International Transaction
    0.08,  # Bank Transfer
    0.07,  # Cash Withdrawal
    0.07,  # Rapid Transactions
    0.06,  # General Transaction
    0.05,  # Card Replacement
    0.04,  # Account Access
]


# Map support issues to the scenario labels.
SCENARIO_MAP = {
    "Duplicate Payment": "duplicate_payment",
    "Failed Payment": "failed_successful_retry",
    "Large Transaction": "large_transaction",
    "Suspicious Transaction": "unusual_location",
    "Rapid Transactions": "rapid_transactions",
}


def load_data():
    """Load customers, transactions and scenario labels."""

    customers = pd.read_csv(CUSTOMERS_PATH)
    transactions = pd.read_csv(TRANSACTIONS_PATH)
    scenario_labels = pd.read_csv(SCENARIO_LABELS_PATH)

    transactions["timestamp"] = pd.to_datetime(
        transactions["timestamp"]
    )

    # Attach scenario information to the transaction data.
    #
    # scenario_labels contains:
    # transaction_id
    # related_transaction_id
    # scenario
    # expected_action
    # requires_human
    #
    # We only need the scenario column for selecting
    # transactions relevant to each support issue.
    transaction_scenarios = scenario_labels[
        ["transaction_id", "scenario"]
    ].drop_duplicates(
        subset=["transaction_id"]
    )

    transactions = transactions.merge(
        transaction_scenarios,
        on="transaction_id",
        how="left"
    )

    # Transactions without an injected scenario are normal transactions.
    transactions["scenario"] = transactions["scenario"].fillna(
        "normal"
    )

    return customers, transactions


def select_transaction(issue_type, transactions):
    """
    Select a transaction relevant to the support issue.

    Scenario-based issues use the ground-truth scenario labels.
    Other transaction issues use a random transaction.
    """

    scenario = SCENARIO_MAP.get(issue_type)

    if scenario:
        matching = transactions[
            transactions["scenario"] == scenario
        ]

        if len(matching) > 0:
            return matching.sample(
                n=1,
                random_state=random.randint(0, 1_000_000)
            ).iloc[0]

    # Fallback for issues without a dedicated scenario.
    return transactions.sample(
        n=1,
        random_state=random.randint(0, 1_000_000)
    ).iloc[0]


def create_description(issue_type, customer, transaction=None):
    """
    Create the customer support description.

    The descriptions contain enough information for the policy
    retrieval system to identify the relevant policy.
    """

    customer_name = (
        f"{customer['first_name']} {customer['last_name']}"
    )

    if issue_type == "Duplicate Payment":
        return (
            f"{customer_name} believes they were charged twice for "
            f"a transaction of {transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']}. "
            f"Please investigate whether this is a duplicate payment."
        )

    elif issue_type == "Refund Request":
        return (
            f"{customer_name} is requesting a refund for a "
            f"{transaction['currency']} {transaction['amount']:.2f} "
            f"transaction at {transaction['merchant']}. "
            f"Please check the transaction status and applicable "
            f"refund rules."
        )

    elif issue_type == "Suspicious Transaction":
        return (
            f"{customer_name} does not recognise a transaction of "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']} in "
            f"{transaction['location']} and believes it may be "
            f"unauthorised. Please investigate the transaction."
        )

    elif issue_type == "Failed Payment":
        return (
            f"{customer_name} had a failed payment of "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']} followed by a successful "
            f"retry. Please investigate the failed payment and "
            f"applicable rules."
        )

    elif issue_type == "Large Transaction":
        return (
            f"{customer_name} has a large transaction of "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']}. "
            f"Please review the transaction and applicable rules."
        )

    elif issue_type == "International Transaction":
        return (
            f"{customer_name} is asking about an international "
            f"transaction of {transaction['currency']} "
            f"{transaction['amount']:.2f} associated with "
            f"{transaction['location']}. "
            f"Please provide information about the transaction "
            f"and any applicable international transaction rules."
        )

    elif issue_type == "Bank Transfer":
        return (
            f"{customer_name} has a question about a bank transfer "
            f"of {transaction['currency']} "
            f"{transaction['amount']:.2f}. "
            f"Please provide information about the transfer "
            f"and any applicable rules."
        )

    elif issue_type == "Cash Withdrawal":
        return (
            f"{customer_name} is asking about a cash withdrawal of "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} in "
            f"{transaction['location']}. "
            f"Please verify the transaction and applicable rules."
        )

    elif issue_type == "Rapid Transactions":
        return (
            f"{customer_name} has several transactions occurring "
            f"within a short period. One transaction was for "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']}. "
            f"Please investigate the rapid transaction activity."
        )

    elif issue_type == "General Transaction":
        return (
            f"{customer_name} has a question about a transaction of "
            f"{transaction['currency']} "
            f"{transaction['amount']:.2f} at "
            f"{transaction['merchant']}. "
            f"Please provide information about the transaction."
        )

    elif issue_type == "Card Replacement":
        return (
            f"{customer_name} is requesting a replacement card. "
            f"Please provide information about the card replacement "
            f"process and required verification."
        )

    elif issue_type == "Account Access":
        return (
            f"{customer_name} is having difficulty accessing their "
            f"account. Please provide information about the account "
            f"access process."
        )

    return (
        f"{customer_name} has a general customer support question. "
        f"Please provide the relevant information."
    )


def generate_support_cases(customers, transactions):
    """Generate the support-case dataset."""

    cases = []

    # Select issue types according to the configured distribution.
    selected_issue_types = random.choices(
        ISSUE_TYPES,
        weights=ISSUE_WEIGHTS,
        k=NUM_CASES,
    )

    transaction_issues = {
        "Duplicate Payment",
        "Refund Request",
        "Suspicious Transaction",
        "Failed Payment",
        "Large Transaction",
        "International Transaction",
        "Bank Transfer",
        "Cash Withdrawal",
        "Rapid Transactions",
        "General Transaction",
    }

    for i, issue_type in enumerate(selected_issue_types):

        # Select a customer.
        customer = customers.sample(
            n=1,
            random_state=random.randint(0, 1_000_000)
        ).iloc[0]

        transaction = None

        # Select a transaction where required.
        if issue_type in transaction_issues:
            transaction = select_transaction(
                issue_type,
                transactions
            )

        description = create_description(
            issue_type,
            customer,
            transaction
        )

        # Generate support-case status.
        status = random.choices(
            [
                "Resolved",
                "Open",
                "In Progress",
                "Escalated",
            ],
            weights=[
                0.45,
                0.25,
                0.20,
                0.10,
            ],
            k=1,
        )[0]

        created_at = fake.date_time_between(
            start_date="-180d",
            end_date="now"
        )

        case = {
            "case_id": f"CASE-{i + 1:05d}",
            "customer_id": customer["customer_id"],
            "transaction_id": (
                transaction["transaction_id"]
                if transaction is not None
                else None
            ),
            "issue_type": issue_type,
            "description": description,
            "status": status,
            "created_at": created_at,
        }

        cases.append(case)

    return pd.DataFrame(cases)


def print_summary(cases):
    """Print summary statistics for the generated dataset."""

    print("\nSupport case dataset created successfully.")
    print("=" * 50)

    print(f"Number of cases: {len(cases):,}")
    print(f"Saved to: {OUTPUT_PATH}")

    print("\nIssue distribution:")
    print(
        cases["issue_type"]
        .value_counts()
        .to_string()
    )

    print("\nCase status:")
    print(
        cases["status"]
        .value_counts()
        .to_string()
    )

    linked_cases = cases["transaction_id"].notna().sum()

    print(
        f"\nTransaction-linked cases: "
        f"{linked_cases:,}/{len(cases):,}"
    )


def main():
    """Generate and save support cases."""

    customers, transactions = load_data()

    cases = generate_support_cases(
        customers,
        transactions
    )

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    cases.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print_summary(cases)


if __name__ == "__main__":
    main()