import random

import numpy as np
import pandas as pd
from faker import Faker


# Keep the generated data reproducible.
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

fake = Faker()
fake.seed_instance(SEED)


# Number of transactions we want to generate.
NUM_TRANSACTIONS = 100_000

CUSTOMER_FILE = "data/raw/customers.csv"
OUTPUT_FILE = "data/raw/transactions.csv"


# Common transaction types in our synthetic banking dataset.
TRANSACTION_TYPES = [
    "Card Payment",
    "Cash Withdrawal",
    "Bank Transfer",
    "Direct Debit",
]


# Most transactions should be completed successfully.
TRANSACTION_STATUSES = [
    "Completed",
    "Failed",
    "Pending",
    "Refunded",
]

TRANSACTION_STATUS_PROBABILITIES = [
    0.88,
    0.05,
    0.04,
    0.03,
]


# Currencies used in the synthetic dataset.
CURRENCIES = [
    "GBP",
    "USD",
    "EUR",
    "INR",
    "CAD",
    "AUD",
]


# A list of merchants gives the agent realistic transaction
# information to reason about later.
MERCHANTS = [
    "Amazon",
    "Tesco",
    "Sainsbury's",
    "ASOS",
    "Apple",
    "Google",
    "Uber",
    "Uber Eats",
    "Deliveroo",
    "Netflix",
    "Spotify",
    "Booking.com",
    "Airbnb",
    "IKEA",
    "Marks & Spencer",
    "John Lewis",
    "Argos",
    "Currys",
    "Shell",
    "BP",
]


# Locations will later help us create suspicious transaction
# patterns such as unusual locations.
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


def generate_transactions(
    customers: pd.DataFrame,
    number_of_transactions: int,
) -> pd.DataFrame:
    """Generate synthetic banking transactions."""

    customer_ids = customers["customer_id"].tolist()

    transactions = []

    for number in range(1, number_of_transactions + 1):

        transaction = {
            "transaction_id": f"T{number:07d}",
            "customer_id": random.choice(customer_ids),
            "timestamp": fake.date_time_between(
                start_date="-1y",
                end_date="now",
            ),
            "merchant": random.choice(MERCHANTS),
            "amount": round(
                np.random.lognormal(
                    mean=3.5,
                    sigma=1.0,
                ),
                2,
            ),
            "currency": random.choice(CURRENCIES),
            "transaction_type": random.choice(TRANSACTION_TYPES),
            "status": np.random.choice(
                TRANSACTION_STATUSES,
                p=TRANSACTION_STATUS_PROBABILITIES,
            ),
            "location": random.choice(LOCATIONS),
        }

        transactions.append(transaction)

    return pd.DataFrame(transactions)


def main() -> None:
    """Load customers, generate transactions, and save them."""

    # Load the customers we generated in the previous step.
    customers = pd.read_csv(CUSTOMER_FILE)

    transactions = generate_transactions(
        customers,
        NUM_TRANSACTIONS,
    )

    transactions.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("Transaction dataset created successfully.")
    print(f"Number of transactions: {len(transactions):,}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nFirst five transactions:")
    print(transactions.head())

    print("\nTransaction status distribution:")
    print(transactions["status"].value_counts())

    print("\nTransaction type distribution:")
    print(transactions["transaction_type"].value_counts())

    print("\nCurrency distribution:")
    print(transactions["currency"].value_counts())

    print("\nTransaction amount statistics:")
    print(transactions["amount"].describe())


if __name__ == "__main__":
    main()