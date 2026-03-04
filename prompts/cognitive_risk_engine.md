Generate a Python module named cognitive_risk_engine.py.

Purpose:
Use an LLM (Gemini) to evaluate behavioral anomalies and produce a risk score.

Requirements:
- Input: normalized context + mock historical behavior
- Output JSON:
  {
    "risk_score": int (0-100),
    "reasoning_log": string,
    "anomaly_flags": [string]
  }

LLM Requirements:
- Prompt must enforce JSON-only output
- Include behavioral heuristics:
  - Amount spike
  - New destination
  - Unusual hour
  - Device/IP mismatch
- Include retry logic (1 retry)
- Timeout: 1 second

Technical Requirements:
- Add guardrail hooks (schema validation)
- Add structured logging:
  - Prompt sent
  - Raw LLM output
  - Parsed output
  - Errors
- Add unit tests:
  - Valid LLM output
  - Invalid JSON → fallback
  - Missing fields
  - Timeout simulation
