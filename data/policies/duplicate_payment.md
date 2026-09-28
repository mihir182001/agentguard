# Duplicate Payment Policy

## Purpose

This policy defines how a possible duplicate card payment
should be investigated.

## Investigation Steps

When a customer reports that they were charged twice:

1. Retrieve the customer's recent transactions.
2. Compare the transactions using:
   - Customer ID
   - Merchant
   - Amount
   - Currency
   - Transaction type
   - Timestamp
3. Two transactions occurring within a short period with
   matching merchant, amount and currency should be treated
   as a possible duplicate.
4. The transactions must be reviewed before any refund is
   recommended.

## Customer Response

If the transactions appear to be a duplicate:

- Explain that the transactions appear to be duplicated.
- Do not claim that a refund has already been issued.
- Explain that the payment requires verification before
  a refund can be processed.

If the transactions do not appear to be duplicated:

- Explain that the available transaction information does
  not confirm a duplicate payment.
- Provide the relevant transaction details.

## Escalation

Escalate the case when:

- Transaction information is incomplete.
- The customer continues to dispute the result.
- A refund decision cannot be made using the available
  information.

## Restrictions

The AI agent must not:

- Automatically issue a refund.
- Modify transaction records.
- Claim that a human has reviewed the case when this has
  not happened.
- Access transactions belonging to another customer.