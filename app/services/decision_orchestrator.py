from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

from app.core.logger import log_info
from app.core.policy_store import get_policy
from app.services import fallback_engine, llm_guardrails
from app.services.cognitive_risk_engine import (
    CognitiveRiskResult,
    LlmCaller,
    assess_cognitive_risk,
)
from app.services.hard_rules_engine import HardRulesResult, NormalizedContext, try_evaluate_hard_rules

MODULE_NAME = "decision_orchestrator"


class DecisionResult(BaseModel):
    """Final orchestrated decision combining hard rules and cognitive risk."""

    decision: Literal["green", "yellow", "red"] = Field(
        ...,
        description="Final decision bucket.",
    )
    next_step: Literal["approve", "hold", "block"] = Field(
        ...,
        description="Recommended operational action.",
    )
    decision_reason: str = Field(
        ...,
        description="Short human-readable reason for this decision.",
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score used for decision mapping.",
    )
    reasoning_log: str = Field(
        ...,
        description="Combined reasoning used for this decision.",
    )
    hard_rules_pass: bool = Field(
        ...,
        description="Whether deterministic hard rules passed.",
    )
    hard_rule_violations: List[str] = Field(
        default_factory=list,
        description="Hard rule violations, if any.",
    )
    anomaly_flags: List[str] = Field(
        default_factory=list,
        description="Anomaly flags coming from cognitive risk and/or fallback.",
    )

    # NEW — required for continuity engine
    used_fallback: bool = False
    fallback_reason: str | None = None


def _map_decision(risk_score: int, thresholds: Dict[str, Any]) -> tuple[str, str]:
    """Map risk_score to (decision, next_step) using policy thresholds."""
    green_threshold = int(thresholds["risk_threshold_green"])
    yellow_threshold = int(thresholds["risk_threshold_yellow"])

    if risk_score < green_threshold:
        return "green", "approve"
    if risk_score <= yellow_threshold:
        return "yellow", "hold"
    return "red", "block"


def orchestrate_decision(
    raw_context: Dict[str, Any],
    mock_history: Dict[str, Any],
    llm: LlmCaller,
) -> DecisionResult:
    """
    Orchestrate the full decision pipeline.
    """
    log_info(
        MODULE_NAME,
        "Decision orchestration started",
        {"raw_context": raw_context, "mock_history": mock_history},
    )

    hard_result: HardRulesResult = try_evaluate_hard_rules(raw_context)

    # -------------------------------
    # HARD RULES FAILURE → FALLBACK
    # -------------------------------
    if not hard_result.hard_rules_pass:
        fallback = fallback_engine.generate_fallback_result(
            reason="hard_rules_failed",
            extra_context={"violations": hard_result.violations},
        )
        thresholds = get_policy()

        decision, next_step = "red", "block"
        decision_reason = "Hard rules violated; transaction must be blocked."

        result = DecisionResult(
            decision=decision,
            next_step=next_step,
            decision_reason=decision_reason,
            risk_score=fallback.risk_score,
            reasoning_log=fallback.reasoning_log,
            hard_rules_pass=False,
            hard_rule_violations=list(hard_result.violations),
            anomaly_flags=fallback.anomaly_flags,
            used_fallback=True,
            fallback_reason="hard_rules_failed",
        )

        log_info(
            MODULE_NAME,
            "Decision path: hard rules failure",
            {
                "thresholds": thresholds,
                "hard_rules_pass": False,
                "violations": hard_result.violations,
                "result": result.dict(),
            },
        )
        return result

    # -------------------------------
    # COGNITIVE RISK + GUARDRAILS
    # -------------------------------
    cognitive: CognitiveRiskResult = assess_cognitive_risk(
        raw_context=raw_context,
        mock_history=mock_history,
        llm=llm,
    )

    guardrail_payload = cognitive.json()
    try:
        llm_guardrails.validate_llm_output(guardrail_payload)
        guardrail_status = "validated"
    except llm_guardrails.LlmValidationError:
        guardrail_status = "failed"
        fallback = fallback_engine.generate_fallback_result(
            reason="guardrail_failed",
            extra_context={"cognitive_result": cognitive.dict()},
        )
        thresholds = get_policy()
        decision, next_step = _map_decision(fallback.risk_score, thresholds)
        decision_reason = (
            f"Guardrails failed; using deterministic fallback risk score {fallback.risk_score} "
            f"mapped to {decision}."
        )
        result = DecisionResult(
            decision=decision,
            next_step=next_step,
            decision_reason=decision_reason,
            risk_score=fallback.risk_score,
            reasoning_log=fallback.reasoning_log,
            hard_rules_pass=True,
            hard_rule_violations=[],
            anomaly_flags=fallback.anomaly_flags,
            used_fallback=True,
            fallback_reason="guardrail_failed",
        )
        log_info(
            MODULE_NAME,
            "Decision path: guardrail fallback",
            {
                "thresholds": thresholds,
                "guardrail_status": guardrail_status,
                "result": result.dict(),
            },
        )
        return result

    # -------------------------------
    # NORMAL COGNITIVE RISK PATH
    # -------------------------------
    thresholds = get_policy()
    decision, next_step = _map_decision(cognitive.risk_score, thresholds)

    decision_reason = (
        f"Risk score {cognitive.risk_score} mapped to {decision} using thresholds "
        f"(green<{thresholds['risk_threshold_green']}, "
        f"yellow<={thresholds['risk_threshold_yellow']})."
    )

    result = DecisionResult(
        decision=decision,
        next_step=next_step,
        decision_reason=decision_reason,
        risk_score=cognitive.risk_score,
        reasoning_log=cognitive.reasoning_log,
        hard_rules_pass=True,
        hard_rule_violations=[],
        anomaly_flags=list(cognitive.anomaly_flags),
        used_fallback=False,
        fallback_reason=None,
    )

    log_info(
        MODULE_NAME,
        "Decision path: cognitive risk",
        {
            "thresholds": {
                "risk_threshold_green": thresholds["risk_threshold_green"],
                "risk_threshold_yellow": thresholds["risk_threshold_yellow"],
                "risk_threshold_red": thresholds.get("risk_threshold_red"),
            },
            "guardrail_status": guardrail_status,
            "hard_rules_pass": True,
            "risk_score": cognitive.risk_score,
            "anomaly_flags": cognitive.anomaly_flags,
        },
    )

    log_info(
        MODULE_NAME,
        "Decision orchestration completed",
        {"result": result.dict()},
    )

    return result
