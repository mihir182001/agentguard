import numpy as np
import pandas as pd


TRANSACTION_FILE = "data/raw/transactions_with_scenarios.csv"
SCENARIO_FILE = "data/processed/scenario_labels.csv"


def validate_duplicate_payments(
    transactions: pd.DataFrame,
    cases: pd.DataFrame,
) -> int:
    """Validate duplicate-payment relationships."""

    valid_cases = 0

    for _, case in cases.iterrows():

        original = transactions[
            transactions["transaction_id"]
            == case["transaction_id"]
        ]

        duplicate = transactions[
            transactions["transaction_id"]
            == case["related_transaction_id"]
        ]

        if original.empty or duplicate.empty:
            continue

        original = original.iloc[0]
        duplicate = duplicate.iloc[0]

        same_customer = (
            original["customer_id"]
            == duplicate["customer_id"]
        )

        same_merchant = (
            original["merchant"]
            == duplicate["merchant"]
        )

        same_amount = np.isclose(
            original["amount"],
            duplicate["amount"],
        )

        same_currency = (
            original["currency"]
            == duplicate["currency"]
        )

        time_difference = abs(
            (
                duplicate["timestamp"]
                - original["timestamp"]
            ).total_seconds()
        )

        close_in_time = time_difference <= 30

        if (
            same_customer
            and same_merchant
            and same_amount
            and same_currency
            and close_in_time
        ):
            valid_cases += 1

    return valid_cases


def validate_large_transactions(
    transactions: pd.DataFrame,
    cases: pd.DataFrame,
) -> int:
    """Validate that large-transaction cases have high amounts."""

    valid_cases = 0

    for _, case in cases.iterrows():

        transaction = transactions[
            transactions["transaction_id"]
            == case["transaction_id"]
        ]

        if transaction.empty:
            continue

        amount = transaction.iloc[0]["amount"]

        if amount >= 1_000:
            valid_cases += 1

    return valid_cases


def validate_unusual_locations(
    transactions: pd.DataFrame,
    cases: pd.DataFrame,
) -> int:
    """Validate that labelled transactions have valid locations."""

    valid_cases = 0

    for _, case in cases.iterrows():

        transaction = transactions[
            transactions["transaction_id"]
            == case["transaction_id"]
        ]

        if transaction.empty:
            continue

        location = transaction.iloc[0]["location"]

        if pd.notna(location) and location != "":
            valid_cases += 1

    return valid_cases


def validate_failed_retries(
    transactions: pd.DataFrame,
    cases: pd.DataFrame,
) -> int:
    """Validate failed transactions followed by successful retries."""

    valid_cases = 0

    for _, case in cases.iterrows():

        failed = transactions[
            transactions["transaction_id"]
            == case["transaction_id"]
        ]

        retry = transactions[
            transactions["transaction_id"]
            == case["related_transaction_id"]
        ]

        if failed.empty or retry.empty:
            continue

        failed = failed.iloc[0]
        retry = retry.iloc[0]

        same_customer = (
            failed["customer_id"]
            == retry["customer_id"]
        )

        same_merchant = (
            failed["merchant"]
            == retry["merchant"]
        )

        same_amount = np.isclose(
            failed["amount"],
            retry["amount"],
        )

        retry_succeeded = (
            failed["status"] == "Failed"
            and retry["status"] == "Completed"
        )

        time_difference = (
            retry["timestamp"]
            - failed["timestamp"]
        ).total_seconds()

        close_in_time = (
            0 < time_difference <= 60
        )

        if (
            same_customer
            and same_merchant
            and same_amount
            and retry_succeeded
            and close_in_time
        ):
            valid_cases += 1

    return valid_cases


def validate_rapid_transactions(
    transactions: pd.DataFrame,
    cases: pd.DataFrame,
) -> int:
    """Validate rapid transaction groups."""

    valid_cases = 0

    for _, case in cases.iterrows():

        original = transactions[
            transactions["transaction_id"]
            == case["transaction_id"]
        ]

        if original.empty:
            continue

        original = original.iloc[0]

        related_ids = str(
            case["related_transaction_id"]
        ).split(",")

        related = transactions[
            transactions["transaction_id"].isin(
                related_ids
            )
        ]

        if len(related) != len(related_ids):
            continue

        same_customer = (
            related["customer_id"]
            == original["customer_id"]
        ).all()

        if not same_customer:
            continue

        time_differences = (
            related["timestamp"]
            - original["timestamp"]
        ).dt.total_seconds().abs()

        if (time_differences <= 40).all():
            valid_cases += 1

    return valid_cases


def print_result(
    scenario_name: str,
    total_cases: int,
    valid_cases: int,
) -> None:
    """Print a validation result."""

    validation_rate = (
        valid_cases / total_cases
    ) * 100

    print(
        f"{scenario_name:<28}"
        f"{valid_cases:>4}/{total_cases:<4}"
        f"  {validation_rate:>6.2f}%"
    )


def main() -> None:
    """Validate every generated scenario."""

    transactions = pd.read_csv(
        TRANSACTION_FILE,
        parse_dates=["timestamp"],
    )

    scenario_labels = pd.read_csv(
        SCENARIO_FILE,
    )

    print("\nAgentGuard Scenario Validation")
    print("=" * 60)

    duplicate_cases = scenario_labels[
        scenario_labels["scenario"]
        == "duplicate_payment"
    ]

    large_cases = scenario_labels[
        scenario_labels["scenario"]
        == "large_transaction"
    ]

    location_cases = scenario_labels[
        scenario_labels["scenario"]
        == "unusual_location"
    ]

    retry_cases = scenario_labels[
        scenario_labels["scenario"]
        == "failed_successful_retry"
    ]

    rapid_cases = scenario_labels[
        scenario_labels["scenario"]
        == "rapid_transactions"
    ]

    duplicate_valid = validate_duplicate_payments(
        transactions,
        duplicate_cases,
    )

    large_valid = validate_large_transactions(
        transactions,
        large_cases,
    )

    location_valid = validate_unusual_locations(
        transactions,
        location_cases,
    )

    retry_valid = validate_failed_retries(
        transactions,
        retry_cases,
    )

    rapid_valid = validate_rapid_transactions(
        transactions,
        rapid_cases,
    )

    print_result(
        "Duplicate payments",
        len(duplicate_cases),
        duplicate_valid,
    )

    print_result(
        "Large transactions",
        len(large_cases),
        large_valid,
    )

    print_result(
        "Unusual locations",
        len(location_cases),
        location_valid,
    )

    print_result(
        "Failed → successful retry",
        len(retry_cases),
        retry_valid,
    )

    print_result(
        "Rapid transactions",
        len(rapid_cases),
        rapid_valid,
    )

    total_cases = len(scenario_labels)

    total_valid = (
        duplicate_valid
        + large_valid
        + location_valid
        + retry_valid
        + rapid_valid
    )

    print("=" * 60)

    print(
        f"Overall validation: "
        f"{total_valid}/{total_cases} "
        f"({(total_valid / total_cases) * 100:.2f}%)"
    )


if __name__ == "__main__":
    main()