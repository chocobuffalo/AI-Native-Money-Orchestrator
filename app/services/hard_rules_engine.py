from __future__ import annotations

from datetime import datetime, time
from typing import List

from pydantic import BaseModel, Field, HttpUrl, ValidationError, validator

from app.core.logger import log_error, log_info
from app.core.policy_store import get_policy

MODULE_NAME = "hard_rules_engine"


class NormalizedContext(BaseModel):
    """Normalized transaction context used as input for Hard Rules Engine."""

    user_id: str = Field(..., description="Unique user identifier")
    amount: float = Field(..., ge=0, description="Transaction amount in smallest currency unit or major unit")
    currency: str = Field(..., min_length=3, max_length=3, description="ISO currency code, e.g., CAD")
    destination: str = Field(..., description="Destination account identifier or type")
    risk_region: str | None = Field(None, description="Region used for risk evaluation")
    channel: str | None = Field(None, description="Channel, e.g., mobile_app, web")
    ip_address: str | None = Field(None, description="IP address of the user")
    device_id: str | None = Field(None, description="Device identifier")
    timestamp: datetime | None = Field(
        None,
        description="Timestamp of the transaction; if omitted, backend time may be used upstream",
    )
    is_kyc_verified: bool | None = Field(
        None,
        description="Mock flag indicating whether the user has passed KYC",
    )
    is_account_blocked: bool | None = Field(
        None,
        description="Mock flag indicating whether the account is blocked for risk reasons",
    )
    destination_country: str | None = Field(
        None,
        description="Destination country for destination-based restrictions",
    )

    @validator("currency")
    def _currency_upper(cls, value: str) -> str:
        return value.upper()

    @validator("destination_country")
    def _country_upper(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None


class HardRulesResult(BaseModel):
    """Deterministic evaluation result for Hard Rules Engine."""

    hard_rules_pass: bool = Field(..., description="True if all hard rules passed")
    violations: List[str] = Field(
        default_factory=list,
        description="List of human-readable violation messages",
    )


def evaluate_hard_rules(context: NormalizedContext) -> HardRulesResult:
    """
    Evaluate deterministic risk rules that must never depend on the LLM.

    This function is pure with respect to decision logic and only relies on
    the policy store for thresholds and configuration.
    """
    policy = get_policy()
    log_info(
        MODULE_NAME,
        "Hard rules evaluation started",
        {"context": context.dict(), "policy": policy},
    )

    violations: List[str] = []

    # Regulatory limits – per transaction cap
    max_amount = float(policy["max_transaction_amount"])
    if context.amount > max_amount:
        violations.append(
            f"Transaction amount {context.amount} exceeds max allowed {max_amount}.",
        )

    # Daily and monthly caps – for the MVP we treat them as contextual flags only.
    # In a real system, this would query aggregate usage; here we only validate amount
    # is not individually above caps to keep logic deterministic without persistence.
    daily_cap = float(policy["daily_cap"])
    if context.amount > daily_cap:
        violations.append(
            f"Transaction amount {context.amount} exceeds daily cap {daily_cap} (mock check).",
        )

    monthly_cap = float(policy["monthly_cap"])
    if context.amount > monthly_cap:
        violations.append(
            f"Transaction amount {context.amount} exceeds monthly cap {monthly_cap} (mock check).",
        )

    # AML / KYC flags – mock flags on context
    if context.is_kyc_verified is False:
        violations.append("User is not KYC verified.")

    # Blocked accounts
    if context.is_account_blocked:
        violations.append("Account is currently blocked for security reasons.")

    # Time-of-day restrictions – example: block transfers between 02:00 and 05:00 UTC
    if context.timestamp is not None:
        tx_time = context.timestamp.time()
        if time(2, 0) <= tx_time < time(5, 0):
            violations.append(
                "Transactions are not allowed between 02:00 and 05:00 UTC (mock rule).",
            )

    # Destination restrictions – example restricted destinations/countries
    restricted_destinations = {"highrisk_exchange", "unknown_wallet"}
    if context.destination.lower() in restricted_destinations:
        violations.append(
            f"Destination '{context.destination}' is restricted for this product.",
        )

    restricted_countries = {"IR", "KP"}
    if context.destination_country is not None and context.destination_country in restricted_countries:
        violations.append(
            f"Destination country '{context.destination_country}' is not supported.",
        )

    hard_rules_pass = len(violations) == 0

    result = HardRulesResult(hard_rules_pass=hard_rules_pass, violations=violations)

    log_info(
        MODULE_NAME,
        "Hard rules evaluation completed",
        {"hard_rules_pass": hard_rules_pass, "violations": violations},
    )
    return result


def try_evaluate_hard_rules(raw_context: dict) -> HardRulesResult:
    """
    Safe wrapper that validates raw input and always returns a HardRulesResult.

    Any validation error is logged and treated as a blocking violation.
    """
    try:
        context = NormalizedContext(**raw_context)
    except ValidationError as exc:
        log_error(
            MODULE_NAME,
            "Validation error in normalized context",
            {"errors": exc.errors()},
        )
        return HardRulesResult(
            hard_rules_pass=False,
            violations=["Invalid normalized context payload."],
        )

    return evaluate_hard_rules(context)

