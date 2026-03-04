from datetime import datetime, timezone

from app.services.hard_rules_engine import (
    HardRulesResult,
    NormalizedContext,
    evaluate_hard_rules,
    try_evaluate_hard_rules,
)


def _base_context() -> dict:
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


def test_happy_path_no_violations() -> None:
    ctx = NormalizedContext(**_base_context())
    result = evaluate_hard_rules(ctx)

    assert isinstance(result, HardRulesResult)
    assert result.hard_rules_pass is True
    assert result.violations == []


def test_amount_above_max_triggers_violation() -> None:
    raw = _base_context()
    raw["amount"] = 6000.0
    ctx = NormalizedContext(**raw)

    result = evaluate_hard_rules(ctx)

    assert result.hard_rules_pass is False
    assert any("exceeds max allowed" in v for v in result.violations)


def test_blocked_account_triggers_violation() -> None:
    raw = _base_context()
    raw["is_account_blocked"] = True
    ctx = NormalizedContext(**raw)

    result = evaluate_hard_rules(ctx)

    assert result.hard_rules_pass is False
    assert "Account is currently blocked for security reasons." in result.violations


def test_time_window_restriction_triggers_violation() -> None:
    raw = _base_context()
    raw["timestamp"] = datetime(2026, 2, 24, 3, 0, 0, tzinfo=timezone.utc)
    ctx = NormalizedContext(**raw)

    result = evaluate_hard_rules(ctx)

    assert result.hard_rules_pass is False
    assert any("02:00 and 05:00 UTC" in v for v in result.violations)


def test_destination_restriction_triggers_violation() -> None:
    raw = _base_context()
    raw["destination"] = "highrisk_exchange"
    ctx = NormalizedContext(**raw)

    result = evaluate_hard_rules(ctx)

    assert result.hard_rules_pass is False
    assert any("Destination 'highrisk_exchange'" in v for v in result.violations)


def test_invalid_payload_returns_failed_result() -> None:
    result = try_evaluate_hard_rules({"amount": -10})

    assert result.hard_rules_pass is False
    assert "Invalid normalized context payload." in result.violations

