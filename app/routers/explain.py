from fastapi import APIRouter, HTTPException, status

from app.core.logger import log_error, log_info
from app.services.status_engine import get_status
from app.services.transparency_layer import generate_explanation, ExplanationResult

MODULE_NAME = "explain_router"

router = APIRouter(prefix="/explain", tags=["Explanation"])


@router.get("/{transaction_id}", response_model=ExplanationResult)
def explain(transaction_id: str) -> ExplanationResult:
    try:
        status_obj = get_status(transaction_id)
    except KeyError:
        log_error(MODULE_NAME, "Unknown transaction_id", {"transaction_id": transaction_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    mapping = {
        "Approved": "green",
        "Held": "yellow",
        "Blocked": "red",
        "Needs Info": "yellow",
    }
    decision_bucket = mapping.get(status_obj.status, "yellow")

    risk_score = status_obj.risk_score or 50
    reasoning_log = status_obj.reasoning_log or f"Transaction currently marked as {status_obj.status}."

    explanation = generate_explanation(
        decision=decision_bucket,
        risk_score=risk_score,
        reasoning_log=reasoning_log,
    )

    log_info(
        MODULE_NAME,
        "Explanation generated",
        {
            "transaction_id": transaction_id,
            "decision_bucket": decision_bucket,
            "risk_score": risk_score,
        },
    )

    return explanation
