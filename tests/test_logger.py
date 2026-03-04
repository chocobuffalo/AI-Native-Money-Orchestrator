import json
from typing import Any, Dict

from app.core.logger import log_error, log_info


def _parse(payload: str) -> Dict[str, Any]:
    return json.loads(payload)


def test_log_info_has_required_fields() -> None:
    payload = log_info("test.module", "hello", {"foo": "bar"})
    data = _parse(payload)

    assert "timestamp" in data
    assert "module" in data
    assert "level" in data
    assert "message" in data
    assert "data" in data

    assert data["module"] == "test.module"
    assert data["level"] == "INFO"
    assert data["message"] == "hello"
    assert data["data"] == {"foo": "bar"}


def test_log_error_sets_error_level() -> None:
    payload = log_error("service.component", "bad things", {"code": 500})
    data = _parse(payload)

    assert data["module"] == "service.component"
    assert data["level"] == "ERROR"
    assert data["message"] == "bad things"
    assert data["data"]["code"] == 500


def test_log_handles_missing_data() -> None:
    payload = log_info("test.module", "no data")
    data = _parse(payload)

    assert isinstance(data["data"], dict)
    assert data["data"] == {}

