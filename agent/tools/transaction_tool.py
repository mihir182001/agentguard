import pandas as pd
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRANSACTION_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "transactions_with_scenarios.csv"
)


class TransactionTool:

    def __init__(self):

        self.transactions = pd.read_csv(
            TRANSACTION_FILE
        )

        self.transactions["transaction_id"] = (
            self.transactions["transaction_id"]
            .astype(str)
        )

        self.transactions["customer_id"] = (
            self.transactions["customer_id"]
            .astype(str)
        )

    def get_transaction(self, transaction_id):

        transaction = self.transactions[
            self.transactions["transaction_id"]
            == str(transaction_id)
        ]

        if transaction.empty:
            return {
                "found": False,
                "transaction_id": str(transaction_id)
            }

        row = transaction.iloc[0]

        return {
            "found": True,
            "transaction_id": str(
                row["transaction_id"]
            ),
            "customer_id": str(
                row["customer_id"]
            ),
            "timestamp": str(
                row["timestamp"]
            ),
            "merchant": row["merchant"],
            "amount": float(
                row["amount"]
            ),
            "currency": row["currency"],
            "transaction_type": row[
                "transaction_type"
            ],
            "status": row["status"],
            "location": row["location"],
        }

    def get_related_transactions(
        self,
        transaction_id,
        limit=10
    ):

        transaction = self.transactions[
            self.transactions["transaction_id"]
            == str(transaction_id)
        ]

        if transaction.empty:
            return []

        row = transaction.iloc[0]

        customer_id = str(row["customer_id"])

        timestamp = pd.to_datetime(
            row["timestamp"]
        )

        customer_transactions = (
            self.transactions[
                self.transactions["customer_id"]
                == customer_id
            ]
            .copy()
        )

        customer_transactions["timestamp"] = (
            pd.to_datetime(
                customer_transactions["timestamp"]
            )
        )

        # Look for transactions within
        # 24 hours of the selected transaction.
        customer_transactions["time_diff"] = (
            (
                customer_transactions["timestamp"]
                - timestamp
            )
            .abs()
            .dt.total_seconds()
        )

        related = (
            customer_transactions[
                (customer_transactions["transaction_id"] != str(transaction_id))
                & (customer_transactions["time_diff"] <= 86400)
            ]
            .sort_values("time_diff")
            .head(limit)
        )

        results = []

        for _, item in related.iterrows():

            results.append(
                {
                    "transaction_id": str(
                        item["transaction_id"]
                    ),
                    "customer_id": str(
                        item["customer_id"]
                    ),
                    "timestamp": str(
                        item["timestamp"]
                    ),
                    "merchant": item["merchant"],
                    "amount": float(
                        item["amount"]
                    ),
                    "currency": item["currency"],
                    "transaction_type": item[
                        "transaction_type"
                    ],
                    "status": item["status"],
                    "location": item["location"],
                    "time_difference_seconds": float(
                        item["time_diff"]
                    ),
                }
            )

        return results


if __name__ == "__main__":

    tool = TransactionTool()

    result = tool.get_transaction(
        "T0000001"
    )

    print("\nTransaction Tool Test")
    print("=" * 60)

    print(result)

    related = tool.get_related_transactions(
        "T0000001"
    )

    print("\nRelated Transactions:")

    for transaction in related[:3]:
        print(transaction)