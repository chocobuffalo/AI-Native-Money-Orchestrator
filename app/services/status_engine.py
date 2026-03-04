from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from app.core.logger import log_error, log_info

MODULE_NAME = "status_engine"

AllowedStatus = Literal["Approved", "Held", "Blocked", "Needs Info"]


class StatusResult(BaseModel):
    """Represents the current status of a transaction."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    status: AllowedStatus = Field(..., description="Current status of the transaction")
    decision_bucket: Optional[str] = Field(
        None,
        description="Decision bucket (green/yellow/red) used for this status, if available.",
    )
    risk_score: Optional[int] = Field(
        None,
        description="Risk score used for the last decision, if available.",
    )
    decision_reason: Optional[str] = Field(
        None,
        description="Short reason for the decision, if available.",
    )
    reasoning_log: Optional[str] = Field(
        None,
        description="Detailed reasoning log from the cognitive engine or fallback.",
    )
    anomaly_flags: List[str] = Field(
        default_factory=list,
        description="Anomaly flags associated with the last decision.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the last status update (UTC).",
    )


_store: Dict[str, StatusResult] = {}
_lock = RLock()


_ALLOWED_TRANSITIONS: Dict[Optional[AllowedStatus], List[AllowedStatus]] = {
    None: ["Approved", "Held", "Blocked", "Needs Info"],
    "Held": ["Approved", "Blocked", "Needs Info"],
    "Needs Info": ["Held", "Approved", "Blocked"],
    "Approved": ["Approved"],
    "Blocked": ["Blocked"],
}


def _validate_transition(
    previous: Optional[AllowedStatus],
    new_status: AllowedStatus,
) -> None:
    allowed = _ALLOWED_TRANSITIONS.get(previous)
    if allowed is None or new_status not in allowed:
        log_error(
            MODULE_NAME,
            "Invalid status transition",
            {"previous": previous, "new_status": new_status, "allowed": allowed},
        )
        raise ValueError(f"Invalid status transition from {previous} to {new_status}")


def set_status(transaction_id: str, status: AllowedStatus) -> StatusResult:
    """
    Set the status for a transaction, enforcing simple MVP transition rules.
    """
    with _lock:
        previous = _store.get(transaction_id)
        previous_status: Optional[AllowedStatus] = previous.status if previous else None

        _validate_transition(previous_status, status)

        result = StatusResult(transaction_id=transaction_id, status=status)
        _store[transaction_id] = result

    log_info(
        MODULE_NAME,
        "Status updated",
        {
            "transaction_id": transaction_id,
            "previous_status": previous_status,
            "new_status": status,
            "updated_at": result.updated_at.isoformat(),
        },
    )
    return result


def set_status_with_decision(
    transaction_id: str,
    status: AllowedStatus,
    decision_bucket: str,
    risk_score: int,
    decision_reason: str,
    reasoning_log: Optional[str],
    anomaly_flags: Optional[List[str]] = None,
) -> StatusResult:
    """
    Set status and attach decision context in a single operation.
    """
    with _lock:
        previous = _store.get(transaction_id)
        previous_status: Optional[AllowedStatus] = previous.status if previous else None

        _validate_transition(previous_status, status)

        result = StatusResult(
            transaction_id=transaction_id,
            status=status,
            decision_bucket=decision_bucket,
            risk_score=risk_score,
            decision_reason=decision_reason,
            reasoning_log=reasoning_log,
            anomaly_flags=anomaly_flags or [],
        )
        _store[transaction_id] = result

    log_info(
        MODULE_NAME,
        "Status with decision updated",
        {
            "transaction_id": transaction_id,
            "previous_status": previous_status,
            "new_status": status,
            "decision_bucket": decision_bucket,
            "risk_score": risk_score,
            "updated_at": result.updated_at.isoformat(),
        },
    )
    return result


def get_status(transaction_id: str) -> StatusResult:
    """Retrieve the current status for a transaction."""
    with _lock:
        result = _store.get(transaction_id)

    if result is None:
        log_error(
            MODULE_NAME,
            "Status read for unknown transaction",
            {"transaction_id": transaction_id},
        )
        raise KeyError(f"Status not found for transaction_id={transaction_id}")

    log_info(
        MODULE_NAME,
        "Status read",
        {
            "transaction_id": transaction_id,
            "status": result.status,
            "updated_at": result.updated_at.isoformat(),
        },
    )
    return result


def list_statuses() -> List[StatusResult]:
    """List all statuses currently stored."""
    with _lock:
        values = list(_store.values())

    log_info(
        MODULE_NAME,
        "Status listing read",
        {"count": len(values)},
    )
    return values


def _reset_store_for_tests() -> None:
    """Internal helper to clear the in-memory store (used in unit tests)."""
    with _lock:
        _store.clear()
