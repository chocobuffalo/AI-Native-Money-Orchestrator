Generate a Python module named fallback_engine.py.

Purpose:
Provide deterministic risk scoring when the LLM fails or guardrails reject the output.

Fallback Logic:
- risk_score = 50 (neutral)
- anomaly_flags = ["fallback"]
- reasoning_log = "Fallback activated due to invalid LLM output."

Output:
{
  "risk_score": 50,
  "reasoning_log": "...",
  "anomaly_flags": ["fallback"]
}

Technical Requirements:
- Add structured logging for fallback activation
- Add unit tests:
  - Always returns deterministic output
  - Logging is triggered
