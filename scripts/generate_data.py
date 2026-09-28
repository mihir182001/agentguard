import random

import numpy as np
import pandas as pd
from faker import Faker


# Keep the generated data reproducible so that the same dataset
# can be recreated whenever the project is run again.
SEED = 42

random.seed(SEED)
np.random.seed(SEED)

fake = Faker()
fake.seed_instance(SEED)


# Number of synthetic customers we want to create.
NUM_CUSTOMERS = 10_000

OUTPUT_FILE = "data/raw/customers.csv"


# These are the account types we will use in our synthetic dataset.
# The probabilities below make the distribution more realistic
# instead of assigning every account type equally.
ACCOUNT_TYPES = [
    "Current",
    "Savings",
    "Premium",
    "Business",
    "Student",
]

ACCOUNT_TYPE_PROBABILITIES = [
    0.50,
    0.25,
    0.10,
    0.05,
    0.10,
]


# Risk levels will later be useful when our AI agent decides
# whether a customer request needs additional review.
RISK_LEVELS = [
    "Low",
    "Medium",
    "High",
]

RISK_PROBABILITIES = [
    0.70,
    0.25,
    0.05,
]


# Most accounts should be active, while a small number can be
# blocked or suspended.
ACCOUNT_STATUSES = [
    "Active",
    "Blocked",
    "Suspended",
]

ACCOUNT_STATUS_PROBABILITIES = [
    0.95,
    0.03,
    0.02,
]


COUNTRIES = [
    "UK",
    "India",
    "USA",
    "Canada",
    "Australia",
]


def generate_customers(number_of_customers: int) -> pd.DataFrame:
    """Generate a synthetic customer dataset."""

    customers = []

    for number in range(1, number_of_customers + 1):

        customer = {
            "customer_id": f"C{number:06d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "country": random.choice(COUNTRIES),
            "account_type": np.random.choice(
                ACCOUNT_TYPES,
                p=ACCOUNT_TYPE_PROBABILITIES,
            ),
            "account_status": np.random.choice(
                ACCOUNT_STATUSES,
                p=ACCOUNT_STATUS_PROBABILITIES,
            ),
            "risk_level": np.random.choice(
                RISK_LEVELS,
                p=RISK_PROBABILITIES,
            ),
            "created_at": fake.date_between(
                start_date="-10y",
                end_date="today",
            ),
        }

        customers.append(customer)

    return pd.DataFrame(customers)


def main() -> None:
    """Generate customers and save them to a CSV file."""

    customers = generate_customers(NUM_CUSTOMERS)

    customers.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("Customer dataset created successfully.")
    print(f"Number of customers: {len(customers):,}")
    print(f"Saved to: {OUTPUT_FILE}")

    print("\nFirst five customers:")
    print(customers.head())

    print("\nAccount type distribution:")
    print(customers["account_type"].value_counts())

    print("\nRisk level distribution:")
    print(customers["risk_level"].value_counts())

    print("\nAccount status distribution:")
    print(customers["account_status"].value_counts())


if __name__ == "__main__":
    main()