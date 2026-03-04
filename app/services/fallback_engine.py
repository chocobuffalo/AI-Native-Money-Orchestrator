from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.core.logger import log_info

MODULE_NAME = "fallback_engine"


class FallbackRiskResult(BaseModel):
    """Deterministic fallback risk result used when the LLM pipeline fails."""

    risk_score: int = Field(50, description="Neutral fallback risk score (0-100)")
    reasoning_log: str = Field(
        "Fallback activated due to invalid LLM output.",
        description="Explanation indicating that deterministic fallback was used.",
    )
    anomaly_flags: List[str] = Field(
        default_factory=lambda: ["fallback"],
        description='Single flag indicating fallback path: ["fallback"].',
    )


def generate_fallback_result(reason: Optional[str] = None, extra_context: Optional[Dict[str, Any]] = None) -> FallbackRiskResult:
    """
    Generate a deterministic fallback result and log its activation.

    The output is always:
        risk_score = 50
        reasoning_log = "Fallback activated due to invalid LLM output."
        anomaly_flags = ["fallback"]
    """
    data: Dict[str, Any] = {"reason": reason} if reason is not None else {}
    if extra_context:
        data["extra_context"] = extra_context

    log_info(
        MODULE_NAME,
        "Fallback engine activated",
        data,
    )

    return FallbackRiskResult()

