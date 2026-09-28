from pathlib import Path
import json
import random
import re
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRANSACTION_FILE = (
    PROJECT_ROOT / "data/raw/transactions_with_scenarios.csv"
)

LABEL_FILE = (
    PROJECT_ROOT / "data/processed/scenario_labels.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "data/fine_tuning"

SEED = 42


SCENARIO_POLICIES = {
    "duplicate_payment": "duplicate_payment.md",
    "large_transaction": "large_transaction.md",
    "unusual_location": "fraud_policy.md",
    "failed_successful_retry": "failed_payment.md",
    "rapid_transactions": "rapid_transaction.md",
}


FROZEN_EVALUATION_IDS = {
    "T0020008",
    "T0100001",
    "T0100501",
    "T0080157",
    "T0032868",
    "T0069223",
}


def clean_text(text):
    text = str(text)

    replacements = {
        "do notperform": "do not perform",
        "paymentreports": "payment reports",
        "subsequentpayment": "subsequent payment",
        "failedpayment": "failed payment",
        "transactioninformation": "transaction information",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = text.replace("-Change", "- Change")
    text = text.replace("-Mark", "- Mark")
    text = text.replace("-Create", "- Create")

    text = text.replace(
        "\n customer",
        "\ncustomer"
    )

    text = text.replace(
        "\n same",
        "\nsame"
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n[ \t]+",
        "\n",
        text
    )

    return text.strip()


def load_data():
    transactions = pd.read_csv(
        TRANSACTION_FILE
    )

    labels = pd.read_csv(
        LABEL_FILE
    )

    return transactions, labels


def get_transaction(
    transactions,
    transaction_id
):
    row = transactions[
        transactions["transaction_id"] == transaction_id
    ]

    if row.empty:
        return None

    return row.iloc[0].to_dict()


def format_transaction(
    transaction
):
    return (
        f"Transaction ID: {transaction['transaction_id']}\n"
        f"Customer ID: {transaction['customer_id']}\n"
        f"Timestamp: {transaction['timestamp']}\n"
        f"Merchant: {transaction['merchant']}\n"
        f"Amount: {transaction['amount']}\n"
        f"Currency: {transaction['currency']}\n"
        f"Transaction Type: {transaction['transaction_type']}\n"
        f"Status: {transaction['status']}\n"
        f"Location: {transaction['location']}"
    )


def load_policy(
    scenario
):
    policy_file = SCENARIO_POLICIES.get(
        scenario
    )

    if policy_file is None:
        return (
            "No specific policy document was supplied."
        )

    path = (
        PROJECT_ROOT
        / "data/policies"
        / policy_file
    )

    if not path.exists():
        return (
            "No specific policy document was supplied."
        )

    policy = path.read_text(
        encoding="utf-8"
    )

    return clean_text(policy)


def build_user_prompt(
    transaction,
    related_transaction,
    scenario,
    policy
):
    prompt = (
        f"Scenario: {scenario}\n\n"
        "Primary transaction:\n"
        f"{format_transaction(transaction)}\n"
    )

    if related_transaction is not None:
        prompt += (
            "\nRelated transaction:\n"
            f"{format_transaction(related_transaction)}\n"
        )

    prompt += (
        "\nApplicable policy:\n"
        f"{policy}\n"
    )

    prompt += (
        "\nDetermine the appropriate enterprise support action. "
        "Use only the supplied transaction evidence and policy. "
        "Do not invent facts, approve financial actions, or change "
        "transaction information."
    )

    return clean_text(prompt)


def build_duplicate_response(
    transaction,
    related_transaction
):
    return {
        "action": "investigate",
        "reason": (
            f"Two transactions for "
            f"{transaction['merchant']} have the same amount "
            f"of {transaction['amount']} "
            f"{transaction['currency']} for the same customer "
            "and occurred close together. This indicates a "
            "possible duplicate payment and requires "
            "investigation rather than an automatic refund."
        ),
        "risk_level": "low",
        "requires_human": False,
        "customer_response": (
            f"We found two similar payments to "
            f"{transaction['merchant']} for "
            f"{transaction['amount']} "
            f"{transaction['currency']} close together. "
            "We will investigate whether the payment was "
            "duplicated."
        )
    }


def build_large_transaction_response(
    transaction
):
    return {
        "action": "inform_customer",
        "reason": (
            f"The transaction amount is "
            f"{transaction['amount']} "
            f"{transaction['currency']}. "
            "A large transaction by itself does not establish "
            "fraud or require the transaction to be blocked."
        ),
        "risk_level": "low",
        "requires_human": False,
        "customer_response": (
            f"The transaction for "
            f"{transaction['amount']} "
            f"{transaction['currency']} to "
            f"{transaction['merchant']} was identified as "
            "a large transaction. A large amount alone does "
            "not confirm fraud."
        )
    }


def build_unusual_location_response(
    transaction
):
    return {
        "action": "investigate",
        "reason": (
            f"The transaction occurred in "
            f"{transaction['location']} for "
            f"{transaction['amount']} "
            f"{transaction['currency']}. "
            "The unusual transaction context is an indicator "
            "for investigation but does not by itself "
            "confirm fraud."
        ),
        "risk_level": "medium",
        "requires_human": False,
        "customer_response": (
            f"We identified a transaction of "
            f"{transaction['amount']} "
            f"{transaction['currency']} to "
            f"{transaction['merchant']} in "
            f"{transaction['location']}. "
            "We will investigate the transaction activity "
            "further."
        )
    }


def build_failed_retry_response(
    transaction,
    related_transaction
):
    return {
        "action": "inform_customer",
        "reason": (
            f"The first "
            f"{transaction['transaction_type']} transaction "
            f"to {transaction['merchant']} for "
            f"{transaction['amount']} "
            f"{transaction['currency']} failed. "
            "A related transaction for the same customer, "
            "merchant and amount subsequently completed. "
            "The evidence indicates a successful retry and "
            "does not support changing the completed "
            "transaction."
        ),
        "risk_level": "low",
        "requires_human": False,
        "customer_response": (
            f"The first payment attempt to "
            f"{transaction['merchant']} for "
            f"{transaction['amount']} "
            f"{transaction['currency']} failed, "
            "but a subsequent payment for the same amount "
            "completed successfully."
        )
    }


def build_rapid_response(
    transaction,
    related_transaction
):
    return {
        "action": "investigate",
        "reason": (
            f"The transaction to "
            f"{transaction['merchant']} for "
            f"{transaction['amount']} "
            f"{transaction['currency']} occurred as part "
            "of rapid transaction activity. Rapid activity "
            "is an investigation indicator but does not "
            "by itself establish fraud."
        ),
        "risk_level": "medium",
        "requires_human": False,
        "customer_response": (
            f"We identified rapid transaction activity "
            f"involving {transaction['merchant']}. "
            "We will investigate the activity further."
        )
    }


def build_assistant_response(
    row,
    transaction,
    related_transaction
):
    scenario = row["scenario"]

    if scenario == "duplicate_payment":
        response = build_duplicate_response(
            transaction,
            related_transaction
        )

    elif scenario == "large_transaction":
        response = build_large_transaction_response(
            transaction
        )

    elif scenario == "unusual_location":
        response = build_unusual_location_response(
            transaction
        )

    elif scenario == "failed_successful_retry":
        response = build_failed_retry_response(
            transaction,
            related_transaction
        )

    elif scenario == "rapid_transactions":
        response = build_rapid_response(
            transaction,
            related_transaction
        )

    else:
        raise ValueError(
            f"Unknown scenario: {scenario}"
        )

    response["reason"] = clean_text(
        response["reason"]
    )

    response["customer_response"] = clean_text(
        response["customer_response"]
    )

    return response


def create_examples(
    transactions,
    labels
):
    examples = []

    for _, row in labels.iterrows():

        transaction_id = row[
            "transaction_id"
        ]

        transaction = get_transaction(
            transactions,
            transaction_id
        )

        if transaction is None:
            continue

        related_transaction = None

        related_id = row[
            "related_transaction_id"
        ]

        if pd.notna(related_id):
            related_transaction = get_transaction(
                transactions,
                related_id
            )

        policy = load_policy(
            row["scenario"]
        )

        user_prompt = build_user_prompt(
            transaction,
            related_transaction,
            row["scenario"],
            policy
        )

        response = build_assistant_response(
            row,
            transaction,
            related_transaction
        )

        example = {
            "transaction_id": transaction_id,
            "related_transaction_id": (
                None
                if pd.isna(related_id)
                else str(related_id)
            ),
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an enterprise financial-support "
                        "decision model. Make evidence-grounded "
                        "decisions and do not perform unauthorized "
                        "financial actions."
                    )
                },
                {
                    "role": "user",
                    "content": user_prompt
                },
                {
                    "role": "assistant",
                    "content": json.dumps(
                        response,
                        ensure_ascii=False
                    )
                }
            ]
        }

        examples.append(
            example
        )

    return examples


def contains_frozen_transaction(
    example
):
    transaction_id = example[
        "transaction_id"
    ]

    related_id = example[
        "related_transaction_id"
    ]

    return (
        transaction_id in FROZEN_EVALUATION_IDS
        or related_id in FROZEN_EVALUATION_IDS
    )


def split_examples(
    examples
):
    frozen = []
    eligible = []

    for example in examples:

        if contains_frozen_transaction(
            example
        ):
            frozen.append(example)
        else:
            eligible.append(example)

    random.seed(SEED)

    random.shuffle(
        eligible
    )

    total = len(eligible)

    train_end = int(
        total * 0.8
    )

    validation_end = int(
        total * 0.9
    )

    train = eligible[
        :train_end
    ]

    validation = eligible[
        train_end:validation_end
    ]

    test = eligible[
        validation_end:
    ]

    test.extend(
        frozen
    )

    random.shuffle(
        test
    )

    return (
        train,
        validation,
        test,
        frozen
    )


def save_jsonl(
    examples,
    path
):
    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        for example in examples:

            output = {
                "messages": example[
                    "messages"
                ]
            }

            file.write(
                json.dumps(
                    output,
                    ensure_ascii=False
                ) + "\n"
            )


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    transactions, labels = load_data()

    examples = create_examples(
        transactions,
        labels
    )

    train, validation, test, frozen = (
        split_examples(examples)
    )

    save_jsonl(
        train,
        OUTPUT_DIR / "train.jsonl"
    )

    save_jsonl(
        validation,
        OUTPUT_DIR / "validation.jsonl"
    )

    save_jsonl(
        test,
        OUTPUT_DIR / "test.jsonl"
    )

    print(
        f"Total examples: {len(examples)}"
    )

    print(
        f"Training examples: {len(train)}"
    )

    print(
        f"Validation examples: {len(validation)}"
    )

    print(
        f"Test examples: {len(test)}"
    )

    print(
        f"Frozen evaluation examples excluded: "
        f"{len(frozen)}"
    )

    print(
        f"Output directory: {OUTPUT_DIR}"
    )

    print(
        "\nFrozen evaluation IDs:"
    )

    for transaction_id in sorted(
        FROZEN_EVALUATION_IDS
    ):
        print(
            f"  {transaction_id}"
        )


if __name__ == "__main__":
    main()