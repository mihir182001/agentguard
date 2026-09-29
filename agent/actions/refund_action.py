def request_refund(customer_id, transaction_id, amount, reason):
    return {
        "action": "refund",
        "customer_id": customer_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "reason": reason,
        "status": "pending_human_approval"
    }