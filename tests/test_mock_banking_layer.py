from typing import Any, Dict, List, Tuple

from app.core import logger
from app.services.mock_banking_layer import MockBankResult, simulate_bank_call


def _capture_logs() -> Tuple[List[Tuple[str, str, Dict[str, Any]]], Any]:
    captured: List[Tuple[str, str, Dict[str, Any]]] = []
    original_log_info = logger.log_info

    def fake_log_info(module: str, message: str, data: Dict[str, Any]) -> str:
        captured.append((module, message, data))
        return "{}"

    logger.log_info = fake_log_info  # type: ignore[assignment]
    return captured, original_log_info


def _restore_logs(original: Any) -> None:
    logger.log_info = original  # type: ignore[assignment]


def test_normal_mode_returns_approved() -> None:
    captured, original = _capture_logs()
    try:
        result = simulate_bank_call("txn-normal", mode="normal")
    finally:
        _restore_logs(original)

    assert isinstance(result, MockBankResult)
    assert result.bank_status == "approved"
    assert result.error_code is None
    assert any(msg == "Mock bank call started" for _, msg, _ in captured)
    assert any(msg == "Mock bank call completed" for _, msg, _ in captured)


def test_slow_mode_returns_approved_with_high_latency() -> None:
    result = simulate_bank_call("txn-slow", mode="slow")

    assert result.bank_status == "approved"
    assert result.error_code is None
    # Slow mode should have latency above the normal window lower bound.
    assert result.latency_ms >= 800


def test_fail_mode_returns_failed_with_error_code() -> None:
    result = simulate_bank_call("txn-fail", mode="fail")

    assert result.bank_status == "failed"
    assert result.error_code is not None


def test_latency_boundaries_for_modes() -> None:
    # We don't control randomness here, but we can assert broad bounds
    # that match the configuration in _simulate_latency.
    normal = simulate_bank_call("txn-n1", mode="normal")
    slow = simulate_bank_call("txn-s1", mode="slow")
    fail = simulate_bank_call("txn-f1", mode="fail")

    assert 0 <= normal.latency_ms <= 1000
    assert slow.latency_ms >= 800
    assert 0 <= fail.latency_ms <= 1500

