Generate a Python module named mock_banking_layer.py.

Purpose:
Simulate bank responses for demo purposes.

Modes:
- normal → approved
- slow → latency spike
- fail → error

Output:
{
  "bank_status": "approved|failed",
  "latency_ms": int,
  "error_code": string | null
}

Technical Requirements:
- Add random latency simulation
- Add structured logging
- Add unit tests for all modes
