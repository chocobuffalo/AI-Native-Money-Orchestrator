from typing import Any, Dict, List, Tuple

from app.core import logger
from app.services.status_engine import (
    AllowedStatus,
    StatusResult,
    _reset_store_for_tests,
    get_status,
    list_statuses,
    set_status,
)


def _capture_logs() -> Tuple[List[Tuple[str, str, Dict[str, Any]]], Any]:
    captured: List[Tuple[str, str, Dict[str, Any]]] = []
    original_log_info = logger.log_info
    original_log_error = logger.log_error

    def fake_log_info(module: str, message: str, data: Dict[str, Any]) -> str:
        captured.append((module, message, data))
        return "{}"

    def fake_log_error(module: str, message: str, data: Dict[str, Any]) -> str:
        captured.append((module, message, data))
        return "{}"

    logger.log_info = fake_log_info  # type: ignore[assignment]
    logger.log_error = fake_log_error  # type: ignore[assignment]
    return captured, (original_log_info, original_log_error)


def _restore_logs(original: Tuple[Any, Any]) -> None:
    original_log_info, original_log_error = original
    logger.log_info = original_log_info  # type: ignore[assignment]
    logger.log_error = original_log_error  # type: ignore[assignment]


def test_valid_transitions() -> None:
    _reset_store_for_tests()
    captured, original = _capture_logs()
    try:
        result1 = set_status("txn-1", "Held")
        result2 = set_status("txn-1", "Approved")
    finally:
        _restore_logs(original)

    assert isinstance(result1, StatusResult)
    assert isinstance(result2, StatusResult)
    assert result2.status == "Approved"
    # Ensure state transition was logged
    assert any(msg == "Status updated" for _, msg, _ in captured)


def test_invalid_transition_from_approved_to_held() -> None:
    _reset_store_for_tests()
    set_status("txn-2", "Approved")

    captured, original = _capture_logs()
    try:
        raised = False
        try:
            set_status("txn-2", "Held")  # not allowed from Approved
        except ValueError:
            raised = True
    finally:
        _restore_logs(original)

    assert raised is True
    # Invalid transitions must be logged
    assert any(
        msg == "Invalid status transition" for _, msg, _ in captured
    )


def test_get_status_retrieval() -> None:
    _reset_store_for_tests()
    created = set_status("txn-3", "Held")

    fetched = get_status("txn-3")

    assert isinstance(fetched, StatusResult)
    assert fetched.transaction_id == "txn-3"
    assert fetched.status == created.status


def test_list_statuses_includes_all_transactions() -> None:
    _reset_store_for_tests()
    set_status("txn-4", "Held")
    set_status("txn-5", "Needs Info")

    items = list_statuses()

    ids = {item.transaction_id for item in items}
    assert "txn-4" in ids
    assert "txn-5" in ids
    assert len(items) >= 2

