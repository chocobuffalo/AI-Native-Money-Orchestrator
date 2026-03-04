from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.core.logger import log_error, log_info
from app.services.hard_rules_engine import NormalizedContext, try_evaluate_hard_rules

MODULE_NAME = "ingest_router"

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=NormalizedContext)
def ingest_transaction(payload: Dict[str, Any]) -> NormalizedContext:
    """
    Ingest a raw transaction payload and return a normalized context.

    This endpoint validates the payload structure using the same NormalizedContext
    model used by the Hard Rules Engine. It also calls try_evaluate_hard_rules to
    ensure the normalized shape is compatible with downstream processing, but it
    does not use the decision outcome at this stage.
    """
    log_info(
        MODULE_NAME,
        "Ingest request received",
        {"received_fields": sorted(payload.keys())},
    )

    try:
        context = NormalizedContext(**payload)
    except ValidationError as exc:
        log_error(
            MODULE_NAME,
            "Invalid transaction payload",
            {"errors": exc.errors()},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction payload",
        )

    # Run through Hard Rules wrapper to validate the normalized context shape.
    # The result is intentionally ignored here as orchestration will handle
    # decision-making later in the pipeline.
    try_evaluate_hard_rules(context.dict())

    log_info(
        MODULE_NAME,
        "Ingest response prepared",
        {
            "user_id": context.user_id,
            "amount": context.amount,
            "currency": context.currency,
            "destination": context.destination,
        },
    )
    return context

