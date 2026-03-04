from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from app.core.logger import log_info

MODULE_NAME = "transparency_layer"

DecisionBucket = Literal["green", "yellow", "red"]


class ExplanationResult(BaseModel):
    """Human-readable explanation of a technical risk decision."""

    user_message: str = Field(..., description="Message shown to the end user.")
    eta: Optional[str] = Field(
        None,
        description="Estimated time until funds are available or review completes.",
    )
    support_hint: str = Field(
        ...,
        description="Short hint guiding the user on what to do if something looks wrong.",
    )


def _base_support_hint() -> str:
    return (
        "If you do not recognize this operation or something looks incorrect, "
        "please contact support from the app."
    )


def _build_green_message(risk_score: int, reasoning_log: Optional[str]) -> ExplanationResult:
    if reasoning_log:
        reason = reasoning_log
    else:
        reason = "Everything looks consistent with your usual activity."

    user_message = (
        "Your transfer has been approved and is being processed. "
        f"Our systems evaluated this operation as low risk (score {risk_score}). "
        f"{reason}"
    )
    return ExplanationResult(
        user_message=user_message,
        eta=None,
        support_hint=_base_support_hint(),
    )


def _build_yellow_message(risk_score: int, reasoning_log: Optional[str]) -> ExplanationResult:
    if reasoning_log:
        reason = reasoning_log
    else:
        reason = (
            "We noticed some details that require a quick safety review before "
            "releasing the funds."
        )

    eta = "within 24 hours"
    user_message = (
        "We are reviewing your transfer for your safety. "
        f"This operation has a moderate risk score ({risk_score}). "
        f"{reason} "
        f"We expect to complete the review {eta}."
    )
    return ExplanationResult(
        user_message=user_message,
        eta=eta,
        support_hint=_base_support_hint(),
    )


def _build_red_message(risk_score: int, reasoning_log: Optional[str]) -> ExplanationResult:
    if reasoning_log:
        reason = reasoning_log
    else:
        reason = (
            "We detected unusual activity that could indicate a security issue."
        )

    user_message = (
        "Your transfer has been blocked for your protection. "
        f"This operation reached a high risk score ({risk_score}). "
        f"{reason}"
    )
    support_hint = (
        "If you did not initiate this operation or think this is a mistake, "
        "please contact support immediately from the app so we can help you."
    )
    return ExplanationResult(
        user_message=user_message,
        eta=None,
        support_hint=support_hint,
    )


def generate_explanation(
    decision: DecisionBucket,
    risk_score: int,
    reasoning_log: Optional[str],
    llm_refiner: Optional[
        callable[[Dict[str, Any]], Dict[str, Any]]
    ] = None,
) -> ExplanationResult:
    """
    Generate a human-readable explanation from a technical decision.

    Optionally passes the structured explanation through an LLM refiner hook
    which can adjust message fields while preserving the overall structure.
    """
    log_info(
        MODULE_NAME,
        "Explanation generation started",
        {
            "decision": decision,
            "risk_score": risk_score,
            "reasoning_log_present": bool(reasoning_log),
        },
    )

    if decision == "green":
        template = "green"
        explanation = _build_green_message(risk_score, reasoning_log)
    elif decision == "yellow":
        template = "yellow"
        explanation = _build_yellow_message(risk_score, reasoning_log)
    else:
        template = "red"
        explanation = _build_red_message(risk_score, reasoning_log)

    log_info(
        MODULE_NAME,
        "Explanation template selected",
        {"decision": decision, "template": template},
    )

    payload = explanation.dict()

    if llm_refiner is not None:
        refined = llm_refiner(payload)
        # Ensure we do not break the contract even if the refiner misbehaves.
        if isinstance(refined, dict):
            payload.update(refined)

    final_explanation = ExplanationResult(**payload)

    log_info(
        MODULE_NAME,
        "Explanation generation completed",
        {"explanation": final_explanation.dict()},
    )

    return final_explanation

