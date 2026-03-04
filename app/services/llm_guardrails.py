from __future__ import annotations

import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field, ValidationError

from app.core.logger import log_error, log_info

MODULE_NAME = "llm_guardrails"


class LlmValidationError(Exception):
    """Raised when LLM output fails guardrail validation."""


class CognitiveRiskSchema(BaseModel):
    """Schema for LLM cognitive risk output."""

    risk_score: int = Field(..., ge=0, le=100)
    reasoning_log: str
    anomaly_flags: List[str] = Field(default_factory=list)


def validate_llm_output(raw_output: str) -> CognitiveRiskSchema:
    """
    Validate raw LLM output against the expected schema.

    - Ensures JSON parses
    - Checks required fields and types
    - Enforces risk_score range 0–100
    """
    log_info(
        MODULE_NAME,
        "LLM output validation started",
        {"raw_output": raw_output},
    )

    try:
        payload: Dict[str, Any] = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        log_error(
            MODULE_NAME,
            "LLM output is not valid JSON",
            {"error": str(exc)},
        )
        raise LlmValidationError("LLM output is not valid JSON") from exc

    try:
        validated = CognitiveRiskSchema(**payload)
    except ValidationError as exc:
        log_error(
            MODULE_NAME,
            "LLM output failed schema validation",
            {"errors": exc.errors()},
        )
        raise LlmValidationError("LLM output does not match expected schema") from exc

    log_info(
        MODULE_NAME,
        "LLM output validation succeeded",
        {"validated": validated.dict()},
    )
    return validated

