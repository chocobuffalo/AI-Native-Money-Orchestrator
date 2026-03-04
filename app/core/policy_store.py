from __future__ import annotations

from threading import RLock
from typing import Any, Dict

from app.core.logger import log_error, log_info

MODULE_NAME = "policy_store"


DEFAULT_POLICY: Dict[str, Any] = {
    "max_transaction_amount": 5000,
    "daily_cap": 10000,
    "monthly_cap": 20000,
    # Thresholds aligned with 3 buckets:
    # 0–30 → green, 31–70 → yellow, 71–100 → red
    "risk_threshold_green": 30,
    "risk_threshold_yellow": 70,
    "risk_threshold_red": 90,
}

_policy: Dict[str, Any] = dict(DEFAULT_POLICY)
_lock = RLock()


def get_policy() -> Dict[str, Any]:
    """
    Return a copy of the full policy configuration.

    Read access is logged in a single event to avoid log noise.
    """
    with _lock:
        current = dict(_policy)

    log_info(
        MODULE_NAME,
        "Policy read",
        {"policy": current},
    )
    return current


def get_value(key: str) -> Any:
    """Return a single policy value, logging the access."""
    with _lock:
        if key not in _policy:
            log_error(
                MODULE_NAME,
                "Attempted to read unknown policy key",
                {"key": key},
            )
            raise KeyError(f"Unknown policy key: {key}")

        value = _policy[key]

    log_info(
        MODULE_NAME,
        "Policy key read",
        {"key": key, "value": value},
    )
    return value


def update_value(key: str, value: Any) -> None:
    """
    Update a single policy value.

    Only keys present in DEFAULT_POLICY are allowed to keep the
    configuration explicit and auditable.
    """
    with _lock:
        if key not in DEFAULT_POLICY:
            log_error(
                MODULE_NAME,
                "Attempted to update unknown policy key",
                {"key": key, "value": value},
            )
            raise KeyError(f"Unknown policy key: {key}")

        old_value = _policy.get(key)
        _policy[key] = value

    log_info(
        MODULE_NAME,
        "Policy key updated",
        {"key": key, "old_value": old_value, "new_value": value},
    )


def reset_defaults() -> None:
    """Reset the in-memory policy to DEFAULT_POLICY and log the operation."""
    with _lock:
        _policy.clear()
        _policy.update(DEFAULT_POLICY)
        snapshot = dict(_policy)

    log_info(
        MODULE_NAME,
        "Policy reset to defaults",
        {"policy": snapshot},
    )
