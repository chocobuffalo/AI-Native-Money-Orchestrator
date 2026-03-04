from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol

from pydantic import BaseModel, Field, ValidationError

from app.core.logger import log_error, log_info
from app.core.policy_store import get_policy
from app.services.hard_rules_engine import NormalizedContext

MODULE_NAME = "cognitive_risk_engine"


class CognitiveRiskResult(BaseModel):
    """Structured cognitive risk assessment returned by the LLM + heuristics."""

    risk_score: int = Field(..., ge=0, le=100, description="Final risk score (0-100)")
    reasoning_log: str = Field(..., description="Natural language reasoning")
    anomaly_flags: List[str] = Field(
        default_factory=list,
        description="List of anomaly flags (e.g., amount_spike, new_destination).",
    )


class LlmStructuredRisk(BaseModel):
    """Schema used as a guardrail for LLM output."""

    risk_score: int = Field(..., ge=0, le=100)
    reasoning_log: str
    anomaly_flags: List[str] = Field(default_factory=list)


class LlmCaller(Protocol):
    """Callable protocol for LLM clients used by this module."""

    def __call__(self, prompt: str, timeout_seconds: float) -> str:  # pragma: no cover - interface
        ...


@dataclass
class BehavioralSignals:
    """Heuristic inputs derived from normalized context + mock history."""

    amount_spike: bool = False
    new_destination: bool = False
    unusual_hour: bool = False
    device_ip_mismatch: bool = False


def _derive_behavioral_signals(context: NormalizedContext, history: Dict[str, Any]) -> BehavioralSignals:
    """
    Derive simple behavioral signals from normalized context and mock history.
    """
    amount = float(context.amount)
    historical_avg_amount = float(history.get("historical_avg_amount", 0.0) or 0.0)
    known_destinations: List[str] = list(history.get("known_destinations", []) or [])
    last_device_id: Optional[str] = history.get("last_device_id")
    last_ip_address: Optional[str] = history.get("last_ip_address")

    amount_spike = False
    if historical_avg_amount > 0 and amount > historical_avg_amount * 3:
        amount_spike = True

    new_destination = False
    if known_destinations and context.destination not in known_destinations:
        new_destination = True

    unusual_hour = False
    if context.timestamp is not None:
        hour = context.timestamp.hour
        if hour < 6 or hour >= 22:
            unusual_hour = True

    device_ip_mismatch = False
    if last_device_id and context.device_id and last_device_id != context.device_id:
        device_ip_mismatch = True
    if last_ip_address and context.ip_address and last_ip_address != context.ip_address:
        device_ip_mismatch = True

    return BehavioralSignals(
        amount_spike=amount_spike,
        new_destination=new_destination,
        unusual_hour=unusual_hour,
        device_ip_mismatch=device_ip_mismatch,
    )


def _build_prompt(context: NormalizedContext, signals: BehavioralSignals) -> str:
    """Create an instruction prompt that enforces JSON-only output."""
    instruction = (
        "You are a risk analysis engine for money movement.\n"
        "You MUST respond with a single JSON object only, no markdown, no text outside JSON.\n"
        "Use the following schema:\n"
        '{\n'
        '  "risk_score": int (0-100),\n'
        '  "reasoning_log": string,\n'
        '  "anomaly_flags": [string]\n'
        "}\n"
        "Consider the behavioral heuristics explicitly:\n"
        "- amount_spike\n"
        "- new_destination\n"
        "- unusual_hour\n"
        "- device_ip_mismatch\n"
    )

    payload = {
        "normalized_context": context.dict(),
        "behavioral_signals": {
            "amount_spike": signals.amount_spike,
            "new_destination": signals.new_destination,
            "unusual_hour": signals.unusual_hour,
            "device_ip_mismatch": signals.device_ip_mismatch,
        },
    }

    return instruction + "\n\nINPUT:\n" + json.dumps(payload, default=str)


def _call_llm_with_retry(prompt: str, llm: LlmCaller, timeout_seconds: float = 1.0) -> str:
    """
    Call the LLM with a single retry on failure or timeout.
    """
    for attempt in range(2):
        try:
            log_info(
                MODULE_NAME,
                "LLM prompt sent",
                {"attempt": attempt + 1, "timeout_seconds": timeout_seconds, "prompt": prompt},
            )
            raw = llm(prompt, timeout_seconds)
            log_info(
                MODULE_NAME,
                "LLM raw output received",
                {"attempt": attempt + 1, "raw_output": raw},
            )
            return raw
        except TimeoutError as exc:
            log_error(
                MODULE_NAME,
                "LLM call timed out",
                {"attempt": attempt + 1, "error": str(exc)},
            )
        except Exception as exc:  # pragma: no cover - defensive
            log_error(
                MODULE_NAME,
                "LLM call failed",
                {"attempt": attempt + 1, "error": str(exc)},
            )
    raise TimeoutError("LLM call failed after retry")


def _parse_llm_output(raw_output: str) -> LlmStructuredRisk:
    """
    Parse and validate LLM JSON using Pydantic as guardrail.
    """
    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        log_error(
            MODULE_NAME,
            "LLM output is not valid JSON",
            {"error": str(exc), "raw_output": raw_output},
        )
        raise

    try:
        parsed = LlmStructuredRisk(**data)
    except ValidationError as exc:
        log_error(
            MODULE_NAME,
            "LLM output failed schema validation",
            {"errors": exc.errors()},
        )
        raise

    log_info(
        MODULE_NAME,
        "LLM parsed output",
        parsed.dict(),
    )
    return parsed


def _apply_heuristics(
    base_score: int,
    signals: BehavioralSignals,
    base_reasoning: Optional[str] = None,
) -> CognitiveRiskResult:
    """
    Combine heuristic signals into a final risk score and anomaly flags.

    This is also used as a fallback when the LLM is unavailable.
    """
    policy = get_policy()

    score = float(base_score)
    anomaly_flags: List[str] = []

    if signals.amount_spike:
        score += 30
        anomaly_flags.append("amount_spike")
    if signals.new_destination:
        score += 20
        anomaly_flags.append("new_destination")
    if signals.unusual_hour:
        score += 15
        anomaly_flags.append("unusual_hour")
    if signals.device_ip_mismatch:
        score += 25
        anomaly_flags.append("device_ip_mismatch")

    score = max(0.0, min(100.0, score))

    reasoning_parts = []
    if base_reasoning:
        reasoning_parts.append(base_reasoning)
    if signals.amount_spike:
        reasoning_parts.append("Detected an amount spike compared to historical behavior.")
    if signals.new_destination:
        reasoning_parts.append("Transfer is going to a new destination.")
    if signals.unusual_hour:
        reasoning_parts.append("Transaction occurs at an unusual hour.")
    if signals.device_ip_mismatch:
        reasoning_parts.append("Device or IP differs from recent activity.")
    if not reasoning_parts:
        reasoning_parts.append("No strong behavioral anomalies detected; risk primarily based on LLM/base score.")

    reasoning_log = " ".join(reasoning_parts)

    thresholds_snapshot = {
        "risk_threshold_green": policy.get("risk_threshold_green"),
        "risk_threshold_yellow": policy.get("risk_threshold_yellow"),
        "risk_threshold_red": policy.get("risk_threshold_red"),
    }

    result = CognitiveRiskResult(
        risk_score=int(score),
        reasoning_log=reasoning_log,
        anomaly_flags=anomaly_flags,
    )

    log_info(
        MODULE_NAME,
        "Heuristic risk evaluation completed",
        {"result": result.dict(), "thresholds": thresholds_snapshot},
    )
    return result


def assess_cognitive_risk(
    raw_context: Dict[str, Any],
    mock_history: Dict[str, Any],
    llm: LlmCaller,
    timeout_seconds: float = 1.0,
) -> CognitiveRiskResult:
    """
    Main entrypoint for cognitive risk evaluation.
    """
    try:
        context = NormalizedContext(**raw_context)
    except ValidationError as exc:
        log_error(
            MODULE_NAME,
            "Invalid normalized context for cognitive risk",
            {"errors": exc.errors()},
        )
        fallback_signals = BehavioralSignals()
        result = _apply_heuristics(base_score=50, signals=fallback_signals, base_reasoning=None)
        result.anomaly_flags.append("invalid_context")
        return result

    signals = _derive_behavioral_signals(context, mock_history)

    prompt = _build_prompt(context, signals)

    try:
        raw_output = _call_llm_with_retry(prompt, llm=llm, timeout_seconds=timeout_seconds)
        structured = _parse_llm_output(raw_output)
        combined = _apply_heuristics(
            base_score=structured.risk_score,
            signals=signals,
            base_reasoning=structured.reasoning_log,
        )
        combined.anomaly_flags = sorted(
            set(combined.anomaly_flags).union(structured.anomaly_flags),
        )
        log_info(
            MODULE_NAME,
            "Cognitive risk evaluation completed",
            {"result": combined.dict()},
        )
        return combined
    except Exception as exc:
        log_error(
            MODULE_NAME,
            "Cognitive risk evaluation fell back to heuristics",
            {"error": str(exc)},
        )
        result = _apply_heuristics(base_score=50, signals=signals, base_reasoning=None)
        result.anomaly_flags.append("fallback_llm_failure")
        return result
