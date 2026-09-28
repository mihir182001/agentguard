# Large Transaction Policy

## Purpose

This policy defines how unusually large transactions should
be reviewed.

## Investigation Steps

When a transaction has an unusually high amount:

1. Retrieve the transaction.
2. Confirm the customer.
3. Check the merchant.
4. Check the currency.
5. Review the transaction status.
6. Determine whether additional review may be required.

## Important Rule

A large transaction is not automatically fraudulent.

The AI agent should report the transaction as an observed
fact and avoid making unsupported conclusions.

## Customer Response

The agent may provide:

- Transaction amount
- Currency
- Merchant
- Transaction status
- Available review information

## Escalation

Escalate when the customer disputes the transaction or
when additional review is required.

## Restrictions

The AI agent must not:

- Automatically block an account.
- Automatically cancel a transaction.
- Declare fraud solely because of transaction size.
- Modify transaction records.