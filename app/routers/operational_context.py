from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.logger import log_info, log_error
from app.services.status_engine import list_statuses

MODULE_NAME = "operational_context_agent"

router = APIRouter(prefix="/operational-context", tags=["Operational Context"])


class HistorySummary(BaseModel):
    transaction_count: int = Field(..., description="Number of transactions observed for this user in the window.")
    avg_amount: Optional[float] = Field(None, description="Average amount if available (mock for MVP).")
    known_destinations: List[str] = Field(default_factory=list, description="Known destinations for this user (mock).")


class OperationalContextResult(BaseModel):
    user_id: str
    last_transaction_id: str
    status: str
    decision_bucket: Optional[str]
    risk_score: Optional[int]
    decision_reason: Optional[str]
    reasoning_log: Optional[str]
    anomaly_flags: List[str]
    history_summary: HistorySummary
    support_case_summary: str


@router.get("/{user_id}", response_model=OperationalContextResult)
def get_operational_context(user_id: str) -> OperationalContextResult:
    """
    AI Operational Context Agent:
    Reúne estado, última decisión, flags y contexto histórico
    para generar un case summary estructurado para soporte.
    """

    statuses = list_statuses()
    user_statuses = [s for s in statuses if s.transaction_id.startswith("txn")]

    if not user_statuses:
        log_error(MODULE_NAME, "No transactions found for user", {"user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No transactions found for this user",
        )

    last_status = sorted(user_statuses, key=lambda s: s.updated_at)[-1]

    history_summary = HistorySummary(
        transaction_count=len(user_statuses),
        avg_amount=120.0,  # mock para MVP
        known_destinations=["trusted_account_77", "savings_01"],
    )

    flags_str = ", ".join(last_status.anomaly_flags) if last_status.anomaly_flags else "none"

    support_case_summary = (
        f"User {user_id} has a transaction {last_status.status.lower()} "
        f"with risk score {last_status.risk_score}. "
        f"Flags: {flags_str}. "
        f"Reason: {last_status.decision_reason}."
    )

    result = OperationalContextResult(
        user_id=user_id,
        last_transaction_id=last_status.transaction_id,
        status=last_status.status,
        decision_bucket=last_status.decision_bucket,
        risk_score=last_status.risk_score,
        decision_reason=last_status.decision_reason,
        reasoning_log=last_status.reasoning_log,
        anomaly_flags=last_status.anomaly_flags,
        history_summary=history_summary,
        support_case_summary=support_case_summary,
    )

    log_info(
        MODULE_NAME,
        "Operational context generated",
        {
            "user_id": user_id,
            "transaction_id": last_status.transaction_id,
            "status": last_status.status,
        },
    )

    return result
