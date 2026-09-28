import random

import numpy as np
import pandas as pd


# Keep the scenario generation reproducible.
SEED = 42

random.seed(SEED)
np.random.seed(SEED)


TRANSACTION_FILE = "data/raw/transactions.csv"

OUTPUT_FILE = "data/raw/transactions_with_scenarios.csv"

SCENARIO_FILE = "data/processed/scenario_labels.csv"


# Number of scenarios we want to inject.
NUM_DUPLICATES = 500
NUM_LARGE_TRANSACTIONS = 300
NUM_UNUSUAL_LOCATIONS = 300
NUM_FAILED_RETRIES = 300
NUM_RAPID_TRANSACTIONS = 300


LOCATIONS = [
    "London",
    "Manchester",
    "Birmingham",
    "Leeds",
    "Liverpool",
    "Bristol",
    "Edinburgh",
    "Glasgow",
    "Dublin",
    "Mumbai",
    "Delhi",
    "New York",
    "Toronto",
    "Sydney",
]


def get_available_transactions(
    transactions: pd.DataFrame,
) -> pd.DataFrame:
    """
    Return completed transactions that have not already been
    used by another scenario.
    """

    return transactions[
        (transactions["status"] == "Completed")
        & (~transactions["_protected"])
    ].copy()


def protect_transactions(
    transactions: pd.DataFrame,
    transaction_ids: set[str],
) -> pd.DataFrame:
    """
    Protect transactions from being modified by later scenarios.
    """

    transactions.loc[
        transactions["transaction_id"].isin(transaction_ids),
        "_protected",
    ] = True

    return transactions


def inject_duplicate_payments(
    transactions: pd.DataFrame,
    number_of_cases: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Create duplicate-payment cases.

    Each duplicate keeps the same customer, merchant, amount,
    currency, and transaction type.

    The duplicate occurs within 5-30 seconds of the original.
    """

    eligible_transactions = get_available_transactions(
        transactions
    )

    selected_transactions = eligible_transactions.sample(
        n=number_of_cases,
        random_state=SEED,
    )

    duplicate_rows = []
    scenario_labels = []

    next_transaction_number = (
        transactions["transaction_id"]
        .str.replace("T", "", regex=False)
        .astype(int)
        .max()
        + 1
    )

    original_ids = set()
    duplicate_ids = set()

    for _, original in selected_transactions.iterrows():

        duplicate = original.copy()

        duplicate_id = f"T{next_transaction_number:07d}"

        duplicate["transaction_id"] = duplicate_id

        duplicate["timestamp"] = (
            pd.to_datetime(original["timestamp"])
            + pd.Timedelta(
                seconds=random.randint(5, 30)
            )
        )

        duplicate_rows.append(duplicate)

        original_id = original["transaction_id"]

        original_ids.add(original_id)
        duplicate_ids.add(duplicate_id)

        scenario_labels.append(
            {
                "transaction_id": original_id,
                "related_transaction_id": duplicate_id,
                "scenario": "duplicate_payment",
                "expected_action": "investigate",
                "requires_human": False,
            }
        )

        next_transaction_number += 1

    duplicate_transactions = pd.DataFrame(
        duplicate_rows
    )

    transactions = pd.concat(
        [
            transactions,
            duplicate_transactions,
        ],
        ignore_index=True,
    )

    # Protect both sides of every duplicate pair.
    transactions = protect_transactions(
        transactions,
        original_ids | duplicate_ids,
    )

    return transactions, scenario_labels


def inject_large_transactions(
    transactions: pd.DataFrame,
    number_of_cases: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Create transactions with unusually large amounts.

    These are labelled as large transactions rather than
    automatically being labelled as fraud.
    """

    eligible_transactions = get_available_transactions(
        transactions
    )

    selected_transactions = eligible_transactions.sample(
        n=number_of_cases,
        random_state=SEED + 1,
    )

    scenario_labels = []

    for index, transaction in selected_transactions.iterrows():

        large_amount = round(
            np.random.uniform(1_000, 5_000),
            2,
        )

        transactions.loc[index, "amount"] = large_amount

        transaction_id = transaction["transaction_id"]

        scenario_labels.append(
            {
                "transaction_id": transaction_id,
                "related_transaction_id": "",
                "scenario": "large_transaction",
                "expected_action": "review",
                "requires_human": False,
            }
        )

    protected_ids = set(
        selected_transactions["transaction_id"]
    )

    transactions = protect_transactions(
        transactions,
        protected_ids,
    )

    return transactions, scenario_labels


def inject_unusual_locations(
    transactions: pd.DataFrame,
    number_of_cases: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Create transactions where the location differs from the
    customer's existing transaction location.
    """

    eligible_transactions = get_available_transactions(
        transactions
    )

    selected_transactions = eligible_transactions.sample(
        n=number_of_cases,
        random_state=SEED + 2,
    )

    scenario_labels = []

    for index, transaction in selected_transactions.iterrows():

        current_location = transaction["location"]

        possible_locations = [
            location
            for location in LOCATIONS
            if location != current_location
        ]

        unusual_location = random.choice(
            possible_locations
        )

        transactions.loc[index, "location"] = (
            unusual_location
        )

        scenario_labels.append(
            {
                "transaction_id": transaction["transaction_id"],
                "related_transaction_id": "",
                "scenario": "unusual_location",
                "expected_action": "investigate",
                "requires_human": False,
            }
        )

    protected_ids = set(
        selected_transactions["transaction_id"]
    )

    transactions = protect_transactions(
        transactions,
        protected_ids,
    )

    return transactions, scenario_labels


def inject_failed_retries(
    transactions: pd.DataFrame,
    number_of_cases: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Create failed payment attempts followed by successful
    retries.
    """

    eligible_transactions = get_available_transactions(
        transactions
    )

    selected_transactions = eligible_transactions.sample(
        n=number_of_cases,
        random_state=SEED + 3,
    )

    retry_rows = []
    scenario_labels = []

    next_transaction_number = (
        transactions["transaction_id"]
        .str.replace("T", "", regex=False)
        .astype(int)
        .max()
        + 1
    )

    protected_ids = set()

    for _, original in selected_transactions.iterrows():

        original_id = original["transaction_id"]

        # Change the original transaction into a failed attempt.
        transactions.loc[
            transactions["transaction_id"] == original_id,
            "status",
        ] = "Failed"

        retry = original.copy()

        retry_id = f"T{next_transaction_number:07d}"

        retry["transaction_id"] = retry_id

        retry["timestamp"] = (
            pd.to_datetime(original["timestamp"])
            + pd.Timedelta(
                seconds=random.randint(10, 60)
            )
        )

        retry["status"] = "Completed"

        retry_rows.append(retry)

        protected_ids.add(original_id)
        protected_ids.add(retry_id)

        scenario_labels.append(
            {
                "transaction_id": original_id,
                "related_transaction_id": retry_id,
                "scenario": "failed_successful_retry",
                "expected_action": "inform_customer",
                "requires_human": False,
            }
        )

        next_transaction_number += 1

    retry_transactions = pd.DataFrame(
        retry_rows
    )

    transactions = pd.concat(
        [
            transactions,
            retry_transactions,
        ],
        ignore_index=True,
    )

    transactions = protect_transactions(
        transactions,
        protected_ids,
    )

    return transactions, scenario_labels


def inject_rapid_transactions(
    transactions: pd.DataFrame,
    number_of_cases: int,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Create groups of transactions that occur within a short
    period of time for the same customer.

    Each scenario contains:

    - one original transaction
    - three additional transactions
    - all four transactions belong to the same customer
    - the additional transactions occur within 30 seconds
      of the original
    """

    scenario_labels = []

    # Keep track of transactions used by rapid-transaction
    # scenarios during this function.
    protected_ids = set()

    # We keep trying until we create the exact number of
    # scenarios requested.
    attempts = 0

    max_attempts = number_of_cases * 20

    while (
        len(scenario_labels) < number_of_cases
        and attempts < max_attempts
    ):
        attempts += 1

        eligible_transactions = get_available_transactions(
            transactions
        )

        if eligible_transactions.empty:
            break

        # Select one transaction to become the centre
        # of the rapid-activity scenario.
        original = eligible_transactions.sample(
            n=1,
            random_state=SEED + attempts,
        ).iloc[0]

        customer_id = original["customer_id"]

        original_time = pd.to_datetime(
            original["timestamp"]
        )

        # Find other available completed transactions
        # belonging to the same customer.
        customer_transactions = transactions[
            (transactions["customer_id"] == customer_id)
            & (transactions["status"] == "Completed")
            & (~transactions["_protected"])
            & (
                transactions["transaction_id"]
                != original["transaction_id"]
            )
        ]

        # We need three additional transactions to create
        # a rapid-transaction pattern.
        if len(customer_transactions) < 3:
            continue

        rapid_transactions = customer_transactions.sample(
            n=3,
            random_state=SEED + attempts + 1000,
        )

        related_ids = []

        for offset, transaction_index in enumerate(
            rapid_transactions.index,
            start=1,
        ):
            # Move the transaction close to the original.
            transactions.loc[
                transaction_index,
                "timestamp",
            ] = (
                original_time
                + pd.Timedelta(
                    seconds=10 * offset
                )
            )

            transaction_id = transactions.loc[
                transaction_index,
                "transaction_id",
            ]

            related_ids.append(transaction_id)

            protected_ids.add(transaction_id)

        # Protect the original transaction too.
        protected_ids.add(
            original["transaction_id"]
        )

        scenario_labels.append(
            {
                "transaction_id": original["transaction_id"],
                "related_transaction_id": ",".join(
                    related_ids
                ),
                "scenario": "rapid_transactions",
                "expected_action": "investigate",
                "requires_human": False,
            }
        )

        # Protect all transactions used by this scenario.
        transactions = protect_transactions(
            transactions,
            protected_ids,
        )

    # Do not silently create fewer cases than requested.
    if len(scenario_labels) != number_of_cases:
        raise RuntimeError(
            f"Could only create "
            f"{len(scenario_labels)} valid rapid-transaction "
            f"scenarios out of {number_of_cases} requested."
        )

    return transactions, scenario_labels


def main() -> None:
    """
    Load transactions, inject all scenarios, and save the
    final dataset and scenario labels.
    """

    # Always start from the original 100,000 transactions.
    #
    # This prevents scenarios from being duplicated if the
    # script is run more than once.
    transactions = pd.read_csv(
        TRANSACTION_FILE,
        parse_dates=["timestamp"],
    )

    # This internal column prevents one scenario from modifying
    # transactions that belong to another scenario.
    transactions["_protected"] = False

    all_labels = []

    # ---------------------------------------------------------
    # Scenario 1: Duplicate payments
    # ---------------------------------------------------------

    transactions, labels = inject_duplicate_payments(
        transactions,
        NUM_DUPLICATES,
    )

    all_labels.extend(labels)

    # ---------------------------------------------------------
    # Scenario 2: Large transactions
    # ---------------------------------------------------------

    transactions, labels = inject_large_transactions(
        transactions,
        NUM_LARGE_TRANSACTIONS,
    )

    all_labels.extend(labels)

    # ---------------------------------------------------------
    # Scenario 3: Unusual locations
    # ---------------------------------------------------------

    transactions, labels = inject_unusual_locations(
        transactions,
        NUM_UNUSUAL_LOCATIONS,
    )

    all_labels.extend(labels)

    # ---------------------------------------------------------
    # Scenario 4: Failed payment followed by retry
    # ---------------------------------------------------------

    transactions, labels = inject_failed_retries(
        transactions,
        NUM_FAILED_RETRIES,
    )

    all_labels.extend(labels)

    # ---------------------------------------------------------
    # Scenario 5: Rapid transactions
    # ---------------------------------------------------------

    transactions, labels = inject_rapid_transactions(
        transactions,
        NUM_RAPID_TRANSACTIONS,
    )

    all_labels.extend(labels)

    # Convert scenario labels into a DataFrame.
    scenario_labels = pd.DataFrame(
        all_labels
    )

    # The protection column is only needed while generating
    # the scenarios. It should not be included in the final data.
    transactions = transactions.drop(
        columns=["_protected"]
    )

    # Keep timestamps in a consistent format.
    transactions["timestamp"] = pd.to_datetime(
        transactions["timestamp"]
    )

    # Save the final transaction dataset.
    transactions.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # Save the ground-truth scenario labels.
    scenario_labels.to_csv(
        SCENARIO_FILE,
        index=False,
    )

    # ---------------------------------------------------------
    # Print summary
    # ---------------------------------------------------------

    print(
        "Scenario injection completed successfully."
    )

    print(
        f"Total transactions: {len(transactions):,}"
    )

    print(
        f"Scenario cases: {len(scenario_labels):,}"
    )

    print(
        f"\nTransactions saved to: {OUTPUT_FILE}"
    )

    print(
        f"Labels saved to: {SCENARIO_FILE}"
    )

    print("\nScenario distribution:")

    print(
        scenario_labels["scenario"].value_counts()
    )

    print("\nExpected action distribution:")

    print(
        scenario_labels["expected_action"].value_counts()
    )

    print("\nHuman escalation distribution:")

    print(
        scenario_labels["requires_human"].value_counts()
    )


if __name__ == "__main__":
    main()