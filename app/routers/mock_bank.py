from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status

from app.core.logger import log_info, log_error
from app.services.mock_banking_layer import simulate_bank_call, MockBankResult

MODULE_NAME = "mock_bank_router"

router = APIRouter(prefix="/bank", tags=["MockBank"])


@router.post("/simulate", response_model=MockBankResult)
def simulate(payload: Dict[str, Any]) -> MockBankResult:
    if "transaction_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="transaction_id is required",
        )

    mode = payload.get("mode", "normal")
    transaction_id = payload["transaction_id"]

    result = simulate_bank_call(transaction_id, mode)

    log_info(
        MODULE_NAME,
        "Mock bank simulation completed",
        {"transaction_id": transaction_id, "mode": mode},
    )

    return result
