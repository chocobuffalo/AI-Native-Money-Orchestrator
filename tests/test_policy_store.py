from typing import Any, Dict, List, Tuple

from app.core import logger
from app.core import policy_store


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


def test_get_policy_returns_copy_and_logs() -> None:
    captured, original = _capture_logs()
    try:
        policy_store.reset_defaults()
        policy = policy_store.get_policy()
    finally:
        _restore_log_info(original)

    assert policy["max_transaction_amount"] == 5000
    # ensure a log was produced for read access
    assert any(msg == "Policy read" for _, msg, _ in captured)


def test_get_value_returns_existing_key_and_logs() -> None:
    captured, original = _capture_logs()
    try:
        policy_store.reset_defaults()
        value = policy_store.get_value("daily_cap")
    finally:
        _restore_log_info(original)

    assert value == 10000
    assert any(
        msg == "Policy key read" and data.get("key") == "daily_cap"
        for _, msg, data in captured
    )


def test_update_value_changes_policy_and_logs() -> None:
    captured, original = _capture_logs()
    try:
        policy_store.reset_defaults()
        policy_store.update_value("monthly_cap", 30000)
        value = policy_store.get_value("monthly_cap")
    finally:
        _restore_log_info(original)

    assert value == 30000
    assert any(
        msg == "Policy key updated" and data.get("key") == "monthly_cap"
        for _, msg, data in captured
    )


def test_update_unknown_key_raises_key_error() -> None:
    policy_store.reset_defaults()
    try:
        raised = False
        try:
            policy_store.update_value("unknown_key", 1)
        except KeyError:
            raised = True
        assert raised is True
    finally:
        # ensure we leave policy in a known state for other tests
        policy_store.reset_defaults()

