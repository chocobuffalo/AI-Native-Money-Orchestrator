from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping, MutableMapping, Optional


def _current_timestamp() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _build_log_entry(
    level: str,
    module: str,
    message: str,
    data: Optional[Mapping[str, Any]] = None,
) -> MutableMapping[str, Any]:
    entry: MutableMapping[str, Any] = {
        "timestamp": _current_timestamp(),
        "module": module,
        "level": level,
        "message": message,
        "data": data if data is not None else {},
    }
    return entry


def _format_log_entry(entry: Mapping[str, Any]) -> str:
    """
    Serialize the log entry as JSON.

    Uses default=str to avoid serialization errors and keep logging resilient.
    """
    return json.dumps(entry, default=str, separators=(",", ":"))


def log_info(
    module: str,
    message: str,
    data: Optional[Mapping[str, Any]] = None,
) -> str:
    """
    Log an informational message as structured JSON.

    Returns the JSON string to facilitate testing and composition.
    """
    entry = _build_log_entry(level="INFO", module=module, message=message, data=data)
    payload = _format_log_entry(entry)
    print(payload)
    return payload


def log_error(
    module: str,
    message: str,
    data: Optional[Mapping[str, Any]] = None,
) -> str:
    """
    Log an error message as structured JSON.

    Returns the JSON string to facilitate testing and composition.
    """
    entry = _build_log_entry(level="ERROR", module=module, message=message, data=data)
    payload = _format_log_entry(entry)
    print(payload)
    return payload
