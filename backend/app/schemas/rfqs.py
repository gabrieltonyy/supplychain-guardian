from datetime import datetime
from enum import Enum

from pydantic import Field

from app.schemas.common import BaseSchema
from app.schemas.execution import RFQLineItem, RFQStatus


class RFQActionType(str, Enum):
    APPROVE = "APPROVE"
    REQUEST_REVIEW = "REQUEST_REVIEW"
    REJECT = "REJECT"


class RFQActionRequest(BaseSchema):
    note: str | None = Field(default=None, max_length=2000)
    actor: str | None = Field(default="procurement_user", max_length=120)


class RFQResponse(BaseSchema):
    id: str
    rfq_id: str
    mitigation_plan_id: str
    workflow_id: str | None = None
    supplier_id: str
    supplier_name: str
    supplier_code: str | None = None
    supplier_email: str
    line_items: list[RFQLineItem] = Field(default_factory=list)
    response_deadline: datetime
    delivery_destination: str
    terms_ref: str
    status: RFQStatus
    price: float | None = None
    currency: str = "USD"
    lead_time_days: int | None = None
    risk_summary: str | None = None
    notes: str | None = None
    version: int
    generated_by: str
    generated_at: datetime
    created_at: datetime
    updated_at: datetime | None = None


class RFQListResponse(BaseSchema):
    success: bool = True
    count: int
    total: int
    limit: int
    offset: int
    rfqs: list[RFQResponse]


class RFQDetailResponse(BaseSchema):
    success: bool = True
    rfq: RFQResponse


class RFQActionHistoryResponse(BaseSchema):
    id: str
    rfq_record_id: str
    rfq_id: str
    action_type: RFQActionType | str
    previous_status: str
    new_status: str
    actor: str
    note: str | None = None
    created_at: datetime


class RFQActionsResponse(BaseSchema):
    success: bool = True
    count: int
    actions: list[RFQActionHistoryResponse]
