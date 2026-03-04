Generate a Python module named decision_orchestrator.py.

Purpose:
Combine Hard Rules + Cognitive Risk + Fallback to produce a final decision.

Decision Logic:
- If hard_rules_pass = false → decision = "red"
- Else:
    - risk_score < 10 → "green"
    - 10 ≤ risk_score ≤ 70 → "yellow"
    - risk_score > 70 → "red"

Output:
{
  "decision": "green|yellow|red",
  "next_step": "approve|hold|escalate",
  "decision_reason": string
}

Technical Requirements:
- Add structured logging for:
  - Inputs
  - Decision path
  - Final output
- Add unit tests:
  - All 3 decision paths
  - Hard rules violation
  - Fallback scenario
