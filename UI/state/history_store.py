history = []

def add_transaction_record(transaction_id, decision):
    history.append({
        "transaction_id": transaction_id,
        "decision": decision
    })

def get_history():
    return history