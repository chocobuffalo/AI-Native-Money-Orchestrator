from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.ingest import router


def _create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


def _valid_payload() -> Dict[str, Any]:
    return {
        "user_id": "user-123",
        "amount": 120.5,
        "currency": "cad",
        "destination": "externalbankaccount",
        "risk_region": "CA",
        "channel": "mobile_app",
        "ip_address": "192.168.0.1",
        "device_id": "device-1",
        "timestamp": datetime(2026, 2, 24, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "is_kyc_verified": True,
        "is_account_blocked": False,
        "destination_country": "CA",
    }


def test_ingest_happy_path_returns_normalized_context() -> None:
    app = _create_app()
    client = TestClient(app)

    response = client.post("/ingest", json=_valid_payload())

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == "user-123"
    assert data["amount"] == 120.5
    # Currency should be normalized to uppercase by NormalizedContext.
    assert data["currency"] == "CAD"
    assert data["destination"] == "externalbankaccount"


def test_ingest_invalid_payload_returns_400() -> None:
    app = _create_app()
    client = TestClient(app)

    # Missing required user_id field.
    invalid_payload = _valid_payload()
    invalid_payload.pop("user_id")

    response = client.post("/ingest", json=invalid_payload)

    assert response.status_code == 400
    body = response.json()
    assert body["detail"] == "Invalid transaction payload"

