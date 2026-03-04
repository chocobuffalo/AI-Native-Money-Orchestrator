Generate a Python module named status_engine.py.

Purpose:
Maintain and update transaction status.

States:
- Approved
- Held
- Blocked
- Needs Info

Requirements:
- Input: transaction_id, decision
- Output: updated status object
- Store status in an in-memory dictionary (MVP)

Technical Requirements:
- Add structured logging for state transitions
- Add unit tests:
  - Valid transitions
  - Invalid transitions
  - State retrieval
