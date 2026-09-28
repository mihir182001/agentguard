# Suspicious Transaction Policy

## Purpose

This policy defines how potentially suspicious transactions
should be handled.

## Investigation Steps

When a customer reports an unfamiliar transaction:

1. Identify the customer.
2. Retrieve the relevant transaction.
3. Check the transaction amount.
4. Check the merchant.
5. Check the transaction location.
6. Review recent transaction activity.
7. Determine whether the available information supports
   further investigation.

## Important Rule

An unusual transaction does not automatically mean that
fraud has occurred.

The AI agent must distinguish between:

- Observed transaction facts.
- Indicators that require investigation.
- Confirmed outcomes.

## Customer Response

The agent should clearly explain what information was found.

For example:

- Transaction amount
- Merchant
- Currency
- Location
- Transaction status

The agent should avoid claiming that fraud has been confirmed
unless the available evidence explicitly supports that claim.

## Escalation

Escalate when:

- The customer disputes the transaction.
- The available information is insufficient.
- Further investigation is required.
- The requested action requires human authorisation.

## Restrictions

The AI agent must not:

- Declare fraud solely because a transaction is unusual.
- Access another customer's transactions.
- Modify transaction records.
- Take unauthorised financial actions.