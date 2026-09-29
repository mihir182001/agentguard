"""
Customer lookup tool.

Provides controlled access to synthetic customer data.
"""

from pathlib import Path

import pandas as pd


CUSTOMER_DATA = Path(
    "data/raw/customers.csv"
)


class CustomerTool:
    """Look up customer information."""

    def __init__(self):
        self.customers = pd.read_csv(
            CUSTOMER_DATA
        )

        self.customers["customer_id"] = (
            self.customers["customer_id"]
            .astype(str)
        )

    def get_customer(self, customer_id):
        """
        Return customer information for a customer ID.
        """

        customer_id = str(customer_id)

        matches = self.customers[
            self.customers["customer_id"]
            == customer_id
        ]

        if matches.empty:
            return {
                "found": False,
                "customer_id": customer_id,
                "message": "Customer not found.",
            }

        customer = matches.iloc[0]

        return {
            "found": True,
            "customer_id": customer["customer_id"],
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "country": customer["country"],
            "account_type": customer["account_type"],
            "account_status": customer["account_status"],
            "risk_level": customer["risk_level"],
            "created_at": customer["created_at"],
        }


if __name__ == "__main__":

    tool = CustomerTool()

    result = tool.get_customer(
        "C000001"
    )

    print("\nCustomer Tool Test")
    print("=" * 60)
    print(result)