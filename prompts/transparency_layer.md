Generate a Python module named transparency_layer.py.

Purpose:
Convert technical decisions into human-readable explanations.

Inputs:
- decision
- risk_score
- reasoning_log

Output:
{
  "user_message": string,
  "eta": string | null,
  "support_hint": string
}

Requirements:
- Use templates for:
  - Green (approved)
  - Yellow (held)
  - Red (blocked)
- Optional: call LLM to refine message

Technical Requirements:
- Add structured logging
- Add unit tests:
  - All 3 decision types
  - Missing reasoning_log
