from datetime import datetime, timezone
from typing import Any, Dict

from app.services.cognitive_risk_engine import (
    CognitiveRiskResult,
    assess_cognitive_risk,
)


def _base_context() -> Dict[str, Any]:
    return {
        "user_id": "user-123",
        "amount": 100.0,
        "currency": "CAD",
        "destination": "trusted_beneficiary",
        "risk_region": "CA",
        "channel": "mobile_app",
        "ip_address": "10.0.0.1",
        "device_id": "device-1",
        "timestamp": datetime(2026, 2, 24, 10, 0, 0, tzinfo=timezone.utc),
        "is_kyc_verified": True,
        "is_account_blocked": False,
        "destination_country": "CA",
    }


def _no_history() -> Dict[str, Any]:
    return {
        "historical_avg_amount": 100.0,
        "known_destinations": ["trusted_beneficiary"],
        "last_device_id": "device-1",
        "last_ip_address": "10.0.0.1",
    }


def test_valid_llm_output_used() -> None:
    def fake_llm(prompt: str, timeout_seconds: float) -> str:
        return '{"risk_score": 10, "reasoning_log": "Low risk", "anomaly_flags": []}'

    result = assess_cognitive_risk(
        raw_context=_base_context(),
        mock_history=_no_history(),
        llm=fake_llm,
    )

    assert isinstance(result, CognitiveRiskResult)
    assert result.risk_score >= 10  # heuristics may increase but not go below


def test_amount_spike_raises_score_and_sets_flag() -> None:
    def fake_llm(prompt: str, timeout_seconds: float) -> str:
        # Very low base score to highlight heuristic effect.
        return '{"risk_score": 0, "reasoning_log": "Base low", "anomaly_flags": []}'

    ctx = _base_context()
    ctx["amount"] = 1000.0
    history = _no_history()
    history["historical_avg_amount"] = 100.0

    result = assess_cognitive_risk(
        raw_context=ctx,
        mock_history=history,
        llm=fake_llm,
    )

    assert result.risk_score > 0
    assert "amount_spike" in result.anomaly_flags


def test_invalid_json_triggers_fallback() -> None:
    def bad_llm(prompt: str, timeout_seconds: float) -> str:
        return "not-json"

    result = assess_cognitive_risk(
        raw_context=_base_context(),
        mock_history=_no_history(),
        llm=bad_llm,
    )

    assert "fallback_llm_failure" in result.anomaly_flags


def test_missing_fields_in_llm_output_trigger_fallback() -> None:
    def incomplete_llm(prompt: str, timeout_seconds: float) -> str:
        # Missing risk_score
        return '{"reasoning_log": "oops", "anomaly_flags": []}'

    result = assess_cognitive_risk(
        raw_context=_base_context(),
        mock_history=_no_history(),
        llm=incomplete_llm,
    )

    assert "fallback_llm_failure" in result.anomaly_flags


def test_timeout_simulation_retries_and_then_falls_back() -> None:
    calls = {"count": 0}

    def timeout_llm(prompt: str, timeout_seconds: float) -> str:
        calls["count"] += 1
        raise TimeoutError("simulated timeout")

    result = assess_cognitive_risk(
        raw_context=_base_context(),
        mock_history=_no_history(),
        llm=timeout_llm,
    )

    assert calls["count"] == 2  # initial + retry
    assert "fallback_llm_failure" in result.anomaly_flags


def test_invalid_context_adds_invalid_context_flag() -> None:
    def fake_llm(prompt: str, timeout_seconds: float) -> str:
        return '{"risk_score": 10, "reasoning_log": "Low", "anomaly_flags": []}'

    # Missing required fields like user_id, amount, etc.
    bad_context: Dict[str, Any] = {}

    result = assess_cognitive_risk(
        raw_context=bad_context,
        mock_history=_no_history(),
        llm=fake_llm,
    )

    assert "invalid_context" in result.anomaly_flags

