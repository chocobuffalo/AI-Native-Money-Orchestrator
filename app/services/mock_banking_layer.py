from __future__ import annotations

import random
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.core.logger import log_info

MODULE_NAME = "mock_banking_layer"

Mode = Literal["normal", "slow", "fail"]


class MockBankResult(BaseModel):
    """Simulated response from a banking provider used for demo purposes."""

    bank_status: Literal["approved", "failed"] = Field(
        ...,
        description='Final status reported by the bank: "approved" or "failed".',
    )
    latency_ms: int = Field(
        ...,
        ge=0,
        description="Simulated latency in milliseconds.",
    )
    error_code: Optional[str] = Field(
        None,
        description="Mock error code when the bank call fails.",
    )


def _simulate_latency(mode: Mode) -> int:
    """Return a simulated latency in milliseconds based on the selected mode."""
    if mode == "normal":
        # Typical latency window for successful calls.
        value = random.uniform(100, 300)
    elif mode == "slow":
        # Latency spike for degraded conditions.
        value = random.uniform(800, 1500)
    else:  # fail
        # Failure may still take some time before timing out.
        value = random.uniform(400, 1200)

    latency = int(value)
    log_info(
        MODULE_NAME,
        "Bank latency simulated",
        {"mode": mode, "latency_ms": latency},
    )
    return latency


def simulate_bank_call(transaction_id: str, mode: Mode = "normal") -> MockBankResult:
    """
    Simulate a bank API call using the provided mode.

    - normal → approved
    - slow → approved but with high latency
    - fail → failed with error_code
    """
    log_info(
        MODULE_NAME,
        "Mock bank call started",
        {"transaction_id": transaction_id, "mode": mode},
    )

    latency_ms = _simulate_latency(mode)

    if mode == "fail":
        result = MockBankResult(
            bank_status="failed",
            latency_ms=latency_ms,
            error_code="BANKTIMEOUT",
        )
    else:
        result = MockBankResult(
            bank_status="approved",
            latency_ms=latency_ms,
            error_code=None,
        )

    log_info(
        MODULE_NAME,
        "Mock bank call completed",
        {
            "transaction_id": transaction_id,
            "mode": mode,
            "result": result.dict(),
        },
    )
    return result

