from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import BaseSchema


class ApprovalStatus(str, Enum):
    """
    Procurement approval states.
    """

    AUTO_APPROVED = "auto_approved"
    PENDING_HUMAN = "pending_human"
    HUMAN_APPROVED = "human_approved"
    REJECTED = "rejected"


class RFQStatus(str, Enum):
    """
    RFQ lifecycle states.
    """

    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REVIEW_REQUESTED = "REVIEW_REQUESTED"
    REJECTED = "REJECTED"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    DISPATCHED = "DISPATCHED"
    RESPONDED = "RESPONDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RFQLineItem(BaseSchema):
    """
    RFQ product/service line item.
    """

    sku: str

    description: str

    quantity: int = Field(
        ...,
        gt=0,
    )

    unit: str

    target_price: float = Field(
        ...,
        ge=0.0,
    )

    notes: str | None = None


class RFQDocument(BaseSchema):
    """
    Generated RFQ document.
    """

    rfq_id: str

    supplier_id: str
    supplier_name: str
    supplier_email: str

    line_items: list[RFQLineItem] = Field(
        default_factory=list
    )

    response_deadline: datetime

    delivery_destination: str

    terms_ref: str

    generated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    version: int = 1

    generated_by: str = "execution_agent"


class DispatchLogEntry(BaseSchema):
    """
    RFQ dispatch tracking.
    """

    rfq_id: str

    channel: str

    sent_at: datetime

    status: str

    recipient: str


class ResponseLogEntry(BaseSchema):
    """
    Supplier response tracking.
    """

    rfq_id: str

    supplier_id: str

    responded_at: datetime

    quote: dict = Field(default_factory=dict)


class ExecutionRecord(BaseSchema):
    """
    Final execution workflow output.
    """

    execution_id: str

    mitigation_plan_id: str

    rfqs: list[RFQDocument] = Field(
        default_factory=list
    )

    approval_status: ApprovalStatus

    approval_decision_at: datetime | None = None

    approved_by: str | None = None

    dispatch_log: list[DispatchLogEntry] = Field(
        default_factory=list
    )

    response_log: list[ResponseLogEntry] = Field(
        default_factory=list
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
