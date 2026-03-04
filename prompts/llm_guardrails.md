Generate a Python module named llm_guardrails.py.

Purpose:
Validate LLM output to ensure safety, correctness, and resilience.

Validation Rules:
- JSON must parse correctly
- Required fields: risk_score, reasoning_log, anomaly_flags
- risk_score must be between 0 and 100
- anomaly_flags must be a list
- reasoning_log must be a string

Output:
- Validated LLM output
- Or a signal to activate fallback

Technical Requirements:
- Raise custom exceptions for invalid output
- Add structured logging for:
  - Validation start
  - Validation errors
  - Final result
- Add unit tests:
  - Valid output
  - Missing fields
  - Wrong types
  - Out-of-range values
