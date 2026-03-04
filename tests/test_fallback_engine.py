from typing import Any, Dict, List, Tuple

from app.core import logger
from app.services.fallback_engine import FallbackRiskResult, generate_fallback_result


def _capture_logs() -> Tuple[List[Tuple[str, str, Dict[str, Any]]], Any]:
    captured: List[Tuple[str, str, Dict[str, Any]]] = []
    original_log_info = logger.log_info

    def fake_log_info(module: str, message: str, data: Dict[str, Any]) -> str:
        captured.append((module, message, data))
        return "{}"

    logger.log_info = fake_log_info  # type: ignore[assignment]
    return captured, original_log_info


def _restore_log_info(original: Any) -> None:
    logger.log_info = original  # type: ignore[assignment]


def test_fallback_result_is_deterministic() -> None:
    result1 = generate_fallback_result(reason="invalid_json")
    result2 = generate_fallback_result(reason="schema_error")

    assert isinstance(result1, FallbackRiskResult)
    assert isinstance(result2, FallbackRiskResult)

    assert result1.risk_score == 50
    assert result2.risk_score == 50
    assert result1.reasoning_log == "Fallback activated due to invalid LLM output."
    assert result2.reasoning_log == "Fallback activated due to invalid LLM output."
    assert result1.anomaly_flags == ["fallback"]
    assert result2.anomaly_flags == ["fallback"]


def test_logging_is_triggered_on_fallback() -> None:
    captured, original = _capture_logs()
    try:
        generate_fallback_result(reason="timeout", extra_context={"attempts": 2})
    finally:
        _restore_log_info(original)

    assert len(captured) >= 1
    modules = {m for m, _, _ in captured}
    messages = {msg for _, msg, _ in captured}

    assert "fallback_engine" in modules
    assert "Fallback engine activated" in messages

