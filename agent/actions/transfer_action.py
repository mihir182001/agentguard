def request_transfer(customer_id, amount, currency, destination):
    return {
        "action": "transfer",
        "customer_id": customer_id,
        "amount": amount,
        "currency": currency,
        "destination": destination,
        "status": "pending_human_approval"
    }