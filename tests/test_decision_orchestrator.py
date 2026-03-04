from datetime import datetime, timezone
from typing import Any, Dict

from app.core import policy_store
from app.services.decision_orchestrator import DecisionResult, orchestrate_decision


def _base_context() -> Dict[str, Any]:
    return {
        "user_id": "user-123",
        "amount": 100.0,
        "currency": "CAD",
        "destination": "trusted_beneficiary",
        "risk_region": "CA",
        "channel": "mobile_app",
        "ip_address": "192.168.0.1",
        "device_id": "device-1",
        "timestamp": datetime(2026, 2, 24, 10, 0, 0, tzinfo=timezone.utc),
        "is_kyc_verified": True,
        "is_account_blocked": False,
        "destination_country": "CA",
    }


def _history() -> Dict[str, Any]:
    return {
        "historical_avg_amount": 100.0,
        "known_destinations": ["trusted_beneficiary"],
        "last_device_id": "device-1",
        "last_ip_address": "192.168.0.1",
    }


def test_green_path() -> None:
    policy_store.reset_defaults()

    def llm(prompt: str, timeout_seconds: float) -> str:
        return '{"risk_score": 0, "reasoning_log": "Very low risk", "anomaly_flags": []}'

    result = orchestrate_decision(
        raw_context=_base_context(),
        mock_history=_history(),
        llm=llm,
    )

    assert isinstance(result, DecisionResult)
    assert result.decision == "green"
    assert result.next_step == "approve"


def test_yellow_path() -> None:
    policy_store.reset_defaults()

    def llm(prompt: str, timeout_seconds: float) -> str:
        return '{"risk_score": 40, "reasoning_log": "Medium risk", "anomaly_flags": []}'

    result = orchestrate_decision(
        raw_context=_base_context(),
        mock_history=_history(),
        llm=llm,
    )

    assert result.decision == "yellow"
    assert result.next_step == "hold"


def test_red_path_from_high_risk_score() -> None:
    policy_store.reset_defaults()

    def llm(prompt: str, timeout_seconds: float) -> str:
        return '{"risk_score": 90, "reasoning_log": "High risk", "anomaly_flags": []}'

    result = orchestrate_decision(
        raw_context=_base_context(),
        mock_history=_history(),
        llm=llm,
    )

    assert result.decision == "red"
    assert result.next_step == "block"


def test_hard_rules_failure_short_circuits_to_red() -> None:
    policy_store.reset_defaults()

    def llm_should_not_be_called(prompt: str, timeout_seconds: float) -> str:  # pragma: no cover - defensive
        raise AssertionError("LLM should not be called when hard rules fail")

    ctx = _base_context()
    # Force hard rules violation (amount above per-transaction cap)
    ctx["amount"] = 6000.0

    result = orchestrate_decision(
        raw_context=ctx,
        mock_history=_history(),
        llm=llm_should_not_be_called,
    )

    assert result.decision == "red"
    assert result.next_step == "block"
    assert result.hard_rules_pass is False
    assert len(result.hard_rule_violations) > 0


def test_fallback_scenario_still_returns_decision() -> None:
    policy_store.reset_defaults()

    calls = {"count": 0}

    def timeout_llm(prompt: str, timeout_seconds: float) -> str:
        calls["count"] += 1
        raise TimeoutError("simulated timeout")

    result = orchestrate_decision(
        raw_context=_base_context(),
        mock_history=_history(),
        llm=timeout_llm,
    )

    assert calls["count"] == 2  # initial + retry inside cognitive_risk_engine
    assert isinstance(result, DecisionResult)
    # We do not assert a specific decision bucket here; we only require
    # that a decision is produced and the pipeline does not crash.
    assert result.decision in ("green", "yellow", "red")

