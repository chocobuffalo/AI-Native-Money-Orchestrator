Generate a Python module named hard_rules_engine.py for a FastAPI backend.

Purpose:
Implement deterministic rules for money movement risk evaluation. These rules must NEVER depend on the LLM.

Requirements:
- Input: normalized transaction context (JSON)
- Rules to implement:
  - Regulatory limits (e.g., max $5,000 per transaction)
  - Daily and monthly caps (mock values)
  - AML/KYC flags (mock)
  - Blocked accounts
  - Time-of-day restrictions
  - Destination restrictions
- Output:
  {
    "hard_rules_pass": bool,
    "violations": [string]
  }

Technical Requirements:
- Use Pydantic models
- Add structured JSON logging for:
  - Input received
  - Rules triggered
  - Violations detected
  - Output returned
- Add unit tests:
  - Happy path
  - Violations triggered
  - Missing fields
  - Boundary values
- Add docstrings and type hints
- No external dependencies beyond FastAPI, Pydantic, Python stdlib
