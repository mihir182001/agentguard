def change_transaction_status(customer_id, transaction_id, new_status):
    return {
        "action": "status_change",
        "customer_id": customer_id,
        "transaction_id": transaction_id,
        "new_status": new_status,
        "status": "pending_human_approval"
    }