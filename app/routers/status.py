from fastapi import APIRouter, HTTPException, status

from app.core.logger import log_info, log_error
from app.services.status_engine import get_status, list_statuses, StatusResult

MODULE_NAME = "status_router"

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/{transaction_id}", response_model=StatusResult)
def read_status(transaction_id: str) -> StatusResult:
    try:
        result = get_status(transaction_id)
        return result
    except KeyError:
        log_error(MODULE_NAME, "Unknown transaction_id", {"transaction_id": transaction_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )


@router.get("", response_model=list[StatusResult])
def read_all_statuses() -> list[StatusResult]:
    log_info(MODULE_NAME, "Listing all statuses", {})
    return list_statuses()
