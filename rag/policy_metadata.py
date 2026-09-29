"""
Policy metadata used by the improved policy retriever.

Each policy contains:
- keywords: explicit words or phrases that indicate the policy
- description: short description of the policy topic
"""

POLICY_METADATA = {

    "duplicate_payment.md": {
        "keywords": [
            "duplicate",
            "charged twice",
            "charged two times",
            "double charge",
            "same payment",
            "same transaction",
            "duplicate payment",
            "duplicate transaction",
        ],
        "description": (
            "Possible duplicate payment where the customer may have "
            "been charged more than once for the same transaction."
        ),
    },

    "refund_policy.md": {
        "keywords": [
            "refund",
            "money back",
            "return payment",
            "refund request",
            "requesting a refund",
            "reimbursement",
            "refunded",
        ],
        "description": (
            "Requests and checks related to transaction refunds."
        ),
    },

    "failed_payment.md": {
        "keywords": [
            "failed payment",
            "payment failed",
            "declined",
            "unsuccessful payment",
            "retry",
            "successful retry",
            "failed transaction",
            "payment was declined",
        ],
        "description": (
            "Payments that failed and cases where a later retry "
            "may have completed successfully."
        ),
    },

    "fraud_policy.md": {
        "keywords": [
            "fraud",
            "fraudulent",
            "suspicious",
            "suspicious transaction",
            "unrecognised",
            "unrecognized",
            "unauthorised",
            "unauthorized",
            "does not recognise",
            "does not recognize",
            "do not recognise",
            "do not recognize",
            "doesn't recognise",
            "doesn't recognize",
            "unrecognised transaction",
            "unrecognized transaction",
            "unauthorised transaction",
            "unauthorized transaction",
            "unknown transaction",
            "unusual transaction",
            "unusual activity",
            "scam",
            "stolen",
        ],
        "description": (
            "Suspicious or potentially unauthorised transactions "
            "that require investigation."
        ),
    },

    "large_transaction.md": {
        "keywords": [
            "large transaction",
            "large payment",
            "unusually large",
            "high value",
            "high-value",
            "large amount",
            "expensive transaction",
            "high amount",
            "large transfer",
        ],
        "description": (
            "Transactions with unusually large monetary amounts "
            "that may require review."
        ),
    },

    "rapid_transaction.md": {
        "keywords": [
            "rapid transactions",
            "rapid transaction",
            "several transactions",
            "multiple transactions",
            "within seconds",
            "within a few seconds",
            "short period",
            "quick transactions",
            "transactions close together",
            "transactions occurring quickly",
            "transactions in quick succession",
            "multiple payments",
        ],
        "description": (
            "Multiple transactions occurring within a short period "
            "of time."
        ),
    },

    "international_transaction.md": {
        "keywords": [
            "international",
            "international transaction",
            "international payment",
            "foreign transaction",
            "foreign payment",
            "overseas transaction",
            "overseas payment",
            "cross-border",
            "cross border",
            "another country",
            "different country",
            "foreign currency",
            "exchange rate",
            "currency conversion",
        ],
        "description": (
            "Transactions involving foreign countries, international "
            "payments, foreign currencies, or cross-border activity."
        ),
    },

    "cash_withdrawal.md": {
        "keywords": [
            "cash withdrawal",
            "cash withdrawal issue",
            "cash machine",
            "ATM",
            "withdrawal",
            "cash",
            "money withdrawn",
            "cash withdrawn",
        ],
        "description": (
            "Issues involving cash withdrawals and ATM transactions."
        ),
    },

    "bank_transfer.md": {
        "keywords": [
            "bank transfer",
            "bank payment",
            "transfer",
            "transferred money",
            "money transfer",
            "recipient",
            "beneficiary",
            "bank transaction",
        ],
        "description": (
            "Issues involving bank transfers and transfer-related "
            "customer requests."
        ),
    },

    "card_replacement.md": {
        "keywords": [
            "replace card",
            "card replacement",
            "replacement card",
            "lost card",
            "stolen card",
            "new card",
            "expired card",
            "card renewal",
        ],
        "description": (
            "Requests to replace a customer's payment card."
        ),
    },
}