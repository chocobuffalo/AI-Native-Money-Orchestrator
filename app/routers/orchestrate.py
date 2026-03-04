from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status

from app.core.logger import log_info, log_error
from app.services.decision_orchestrator import orchestrate_decision, DecisionResult
from app.services.status_engine import set_status_with_decision
from app.services.hard_rules_engine import NormalizedContext
from app.services.continuity_engine import continuity_engine, ContinuityEvent

MODULE_NAME = "orchestrate_router"

router = APIRouter(prefix="/orchestrate", tags=["Decision"])


# Simple LLM stub for MVP
def stub_llm(prompt: str, timeout_seconds: float) -> str:
    return '{"risk_score": 20, "reasoning_log": "stub", "anomaly_flags": []}'


@router.post("", response_model=DecisionResult)
def orchestrate(payload: Dict[str, Any]) -> DecisionResult:
    """
    Full decision orchestration endpoint with continuity & failure mode tracking.
    """
    log_info(
        MODULE_NAME,
        "Orchestration request received",
        {"keys": sorted(payload.keys())},
    )

    # -------------------------------
    # Validate transaction_id
    # -------------------------------
    if "transaction_id" not in payload:
        log_error(MODULE_NAME, "Missing transaction_id", {})

        continuity_engine.record(
            ContinuityEvent(
                event_type="error",
                source="orchestrator",
                description="Missing transaction_id in request"
            )
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_id is required",
        )

    transaction_id = payload["transaction_id"]
    raw_context = payload.get("raw_context")
    mock_history = payload.get("mock_history")

    # -------------------------------
    # Validate context shape
    # -------------------------------
    if not isinstance(raw_context, dict) or not isinstance(mock_history, dict):
        continuity_engine.record(
            ContinuityEvent(
                event_type="error",
                source="orchestrator",
                description="raw_context or mock_history invalid type"
            )
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="raw_context and mock_history must be objects",
        )

    try:
        NormalizedContext(**raw_context)
    except Exception as exc:
        log_error(MODULE_NAME, "Invalid raw_context", {"error": str(exc)})

        continuity_engine.record(
            ContinuityEvent(
                event_type="error",
                source="guardrails",
                description="Context validation failed",
                metadata={"error": str(exc)}
            )
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid raw_context",
        )

    # -------------------------------
    # Run the full decision pipeline
    # -------------------------------
    try:
        decision_result = orchestrate_decision(
            raw_context=raw_context,
            mock_history=mock_history,
            llm=stub_llm,
        )
    except Exception as exc:
        log_error(MODULE_NAME, "Pipeline failure", {"error": str(exc)})

        continuity_engine.record(
            ContinuityEvent(
                event_type="error",
                source="orchestrator",
                description="Decision pipeline crashed",
                metadata={"error": str(exc)}
            )
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Decision pipeline failed",
        )

    # -------------------------------
    # Map next_step → Status Engine
    # -------------------------------
    mapping = {
        "approve": "Approved",
        "hold": "Held",
        "block": "Blocked",
    }
    final_status = mapping[decision_result.next_step]

    # -------------------------------
    # Store full decision context
    # -------------------------------
    set_status_with_decision(
        transaction_id=transaction_id,
        status=final_status,
        decision_bucket=decision_result.decision,
        risk_score=decision_result.risk_score,
        decision_reason=decision_result.decision_reason,
        reasoning_log=decision_result.reasoning_log,
        anomaly_flags=decision_result.anomaly_flags,
    )

    # -------------------------------
    # Continuity tracking: fallback or degraded mode
    # -------------------------------
    if decision_result.used_fallback:
        continuity_engine.record(
            ContinuityEvent(
                event_type="fallback",
                source="llm",
                description="LLM failed, fallback heuristics used",
                metadata={"reason": decision_result.fallback_reason}
            )
        )

    # -------------------------------
    # Continuity tracking: success
    # -------------------------------
    continuity_engine.record(
        ContinuityEvent(
            event_type="info",
            source="orchestrator",
            description="Decision pipeline completed successfully",
            metadata={
                "transaction_id": transaction_id,
                "decision": decision_result.decision,
                "status": final_status,
            }
        )
    )

    log_info(
        MODULE_NAME,
        "Orchestration completed",
        {
            "transaction_id": transaction_id,
            "decision": decision_result.decision,
            "next_step": decision_result.next_step,
            "status_set": final_status,
        },
    )

    return decision_result
