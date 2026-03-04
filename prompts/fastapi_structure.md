Generate a FastAPI project structure with:

/app
  /routers
    ingest.py
    score.py
    orchestrate.py
    status.py
    explain.py
    mock_bank.py
  /core
    logger.py
    policy_store.py
  /services
    hard_rules_engine.py
    cognitive_risk_engine.py
    llm_guardrails.py
    fallback_engine.py
    decision_orchestrator.py
    status_engine.py
    transparency_layer.py
    mock_banking_layer.py
  models.py
  main.py

Requirements:
- Each router calls the appropriate service
- Add logging in every endpoint
- Add error handling
- Add OpenAPI tags
