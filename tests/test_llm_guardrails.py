from app.services.llm_guardrails import (
    CognitiveRiskSchema,
    LlmValidationError,
    validate_llm_output,
)


def test_valid_output_passes_validation() -> None:
    raw = '{"risk_score": 20, "reasoning_log": "Looks fine", "anomaly_flags": []}'
    result = validate_llm_output(raw)

    assert isinstance(result, CognitiveRiskSchema)
    assert result.risk_score == 20
    assert result.reasoning_log == "Looks fine"
    assert result.anomaly_flags == []


def test_missing_fields_raise_validation_error() -> None:
    raw = '{"risk_score": 20, "anomaly_flags": []}'  # missing reasoning_log

    raised = False
    try:
        validate_llm_output(raw)
    except LlmValidationError:
        raised = True

    assert raised is True


def test_wrong_types_raise_validation_error() -> None:
    raw = '{"risk_score": "high", "reasoning_log": 123, "anomaly_flags": "oops"}'

    raised = False
    try:
        validate_llm_output(raw)
    except LlmValidationError:
        raised = True

    assert raised is True


def test_out_of_range_risk_score_raises_validation_error() -> None:
    raw = '{"risk_score": 150, "reasoning_log": "Too high", "anomaly_flags": []}'

    raised = False
    try:
        validate_llm_output(raw)
    except LlmValidationError:
        raised = True

    assert raised is True

