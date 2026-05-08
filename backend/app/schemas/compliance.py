import hashlib
import json
from datetime import datetime, UTC
from enum import Enum
from typing import Any

from pydantic import Field

from app.schemas.common import BaseSchema


class SanctionsHitSeverity(str, Enum):
    """
    Sanctions screening severity.
    """

    CLEAR = "clear"
    ADVISORY = "advisory"
    BLOCKED = "blocked"


class RegulatoryCheck(str, Enum):
    """
    Supported regulatory validation checks.
    """

    GDPR_DATA_TRANSFER = "gdpr_data_transfer"
    EXPORT_CONTROL = "export_control"
    TRADE_RESTRICTION = "trade_restriction"
    TARIFF_CLASSIFICATION = "tariff_classification"
    DUAL_USE_GOODS = "dual_use_goods"


class ComplianceVerdict(str, Enum):
    """
    Final compliance decision.
    """

    CLEARED = "cleared"
    FLAGGED = "flagged"
    BLOCKED = "blocked"


class SanctionsResult(BaseSchema):
    """
    Supplier sanctions screening result.
    """

    supplier_id: str
    supplier_name: str
    supplier_country: str

    hit_severity: SanctionsHitSeverity

    matched_lists: list[str] = Field(default_factory=list)

    match_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    screened_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class RegulatoryResult(BaseSchema):
    """
    Deterministic regulatory check result.
    """

    check_type: RegulatoryCheck

    passed: bool

    details: str

    applicable_regulation: str

    remediation: str | None = None


class AuditLogEntry(BaseSchema):
    """
    Immutable compliance audit log payload.
    """

    log_id: str

    workflow_run_id: str

    agent_id: str = "compliance_agent"

    agent_version: str

    execution_record_id: str

    input_hash: str

    sanctions_results: list[SanctionsResult] = Field(default_factory=list)

    regulatory_results: list[RegulatoryResult] = Field(default_factory=list)

    verdict: ComplianceVerdict

    verdict_rationale: str

    llm_summary: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    @classmethod
    def compute_input_hash(
        cls,
        execution_record: dict[str, Any],
    ) -> str:
        """
        Compute SHA-256 hash of canonical execution record JSON.
        """

        canonical = json.dumps(
            execution_record,
            sort_keys=True,
            default=str,
        )

        return hashlib.sha256(
            canonical.encode("utf-8")
        ).hexdigest()