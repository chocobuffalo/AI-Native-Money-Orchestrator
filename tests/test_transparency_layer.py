from typing import Any, Dict

from app.services.transparency_layer import (
    ExplanationResult,
    generate_explanation,
)


def test_green_explanation_includes_approved_language() -> None:
    result = generate_explanation(
        decision="green",
        risk_score=5,
        reasoning_log="User frequently sends similar amounts.",
    )

    assert isinstance(result, ExplanationResult)
    assert "approved" in result.user_message.lower()
    assert "low risk" in result.user_message.lower()
    assert result.eta is None


def test_yellow_explanation_includes_eta_and_review_language() -> None:
    result = generate_explanation(
        decision="yellow",
        risk_score=40,
        reasoning_log="First time sending to this destination.",
    )

    assert "reviewing your transfer" in result.user_message
    assert result.eta is not None
    assert "24 hours" in result.user_message


def test_red_explanation_includes_blocked_and_support_hint() -> None:
    result = generate_explanation(
        decision="red",
        risk_score=85,
        reasoning_log="Large withdrawal after password change.",
    )

    assert "blocked" in result.user_message.lower()
    assert "high risk" in result.user_message.lower()
    assert "contact support" in result.support_hint.lower()


def test_missing_reasoning_log_uses_default_copy() -> None:
    result_green = generate_explanation(
        decision="green",
        risk_score=3,
        reasoning_log=None,
    )
    result_yellow = generate_explanation(
        decision="yellow",
        risk_score=30,
        reasoning_log="",
    )
    result_red = generate_explanation(
        decision="red",
        risk_score=90,
        reasoning_log=None,
    )

    assert "everything looks consistent" in result_green.user_message.lower()
    assert "require a quick safety review" in result_yellow.user_message.lower()
    assert "unusual activity" in result_red.user_message.lower()

