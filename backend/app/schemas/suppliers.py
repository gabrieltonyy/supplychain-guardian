from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import BaseSchema


class SupplierStatus(str, Enum):
    """
    Supplier operational status.
    """

    ACTIVE = "active"
    DORMANT = "dormant"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class ComplianceStatus(str, Enum):
    """
    Supplier compliance status.
    """

    APPROVED = "approved"
    PENDING_REVIEW = "pending_review"
    EXCLUDED = "excluded"
    BLOCKED = "blocked"


class RelationshipStatus(str, Enum):
    """
    Business relationship status with supplier.
    """

    ACTIVE_SECONDARY = "active_secondary"
    DORMANT = "dormant"
    NEW = "new"


class SupplierProfile(BaseSchema):
    """
    Supplier profile used by discovery, simulation, and execution agents.
    """

    id: str
    name: str

    country: str
    region: str

    contact_email: str | None = None

    product_categories: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

    status: SupplierStatus = SupplierStatus.ACTIVE
    compliance_status: ComplianceStatus = ComplianceStatus.APPROVED
    relationship_status: RelationshipStatus = RelationshipStatus.NEW

    unit_cost: float | None = None
    typical_lead_time_days: int | None = None
    capacity_units_per_month: int | None = None

    on_time_delivery_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    quality_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    latest_risk_score: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
    )

    embedding_refreshed_at: datetime | None = None


class SupplierSearchRequest(BaseSchema):
    """
    Request payload for supplier search/discovery.
    """

    product_categories: list[str]
    exclude_regions: list[str] = Field(default_factory=list)
    min_capacity_pct: float = Field(default=0.7, ge=0.0, le=1.0)
    compliance_status: ComplianceStatus = ComplianceStatus.APPROVED
    top_k: int = Field(default=5, ge=1, le=20)


class SupplierSearchResult(BaseSchema):
    """
    Supplier discovery result.
    """

    supplier: SupplierProfile
    similarity_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    passed_hard_filter: bool = True
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)