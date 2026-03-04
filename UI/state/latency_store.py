latency_records = []

def add_latency_record(transaction_id, mode, latency_ms):
    latency_records.append({
        "transaction_id": transaction_id,
        "mode": mode,
        "latency_ms": latency_ms
    })

def get_latency_records():
    return latency_records