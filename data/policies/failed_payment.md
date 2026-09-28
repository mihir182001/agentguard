# Failed Payment Policy

## Purpose

This policy defines how failed payment reports should
be investigated.

## Investigation Steps

When a customer reports a failed payment:

1. Identify the customer's transaction.
2. Check the transaction status.
3. Look for a later transaction involving the same
   customer, merchant and amount.
4. Check whether the later transaction completed
   successfully.

## Successful Retry

If a failed transaction is followed by a successful
transaction:

- Inform the customer that a later payment was completed.
- Provide the relevant transaction information.
- Do not treat the failed transaction as a completed
  payment.

## No Successful Retry

If there is no successful retry:

- Explain that the available transaction shows as failed.
- Do not claim that the payment was completed.

## Escalation

Escalate when the transaction history is inconsistent
or insufficient to determine what happened.

## Restrictions

The AI agent must not:

- Change transaction status.
- Mark a failed transaction as successful.
- Create a new payment.
- Claim that a payment succeeded without evidence.