from datetime import datetime
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class BaseSchema(BaseModel):
    """
    Shared base schema.
    """

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
    }


class TimestampMixin(BaseSchema):
    """
    Standard timestamp fields.
    """

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class PaginationMeta(BaseSchema):
    """
    Pagination metadata.
    """

    page: int
    page_size: int
    total_items: int
    total_pages: int


class SuccessResponse(BaseSchema, Generic[T]):
    """
    Standard API success response wrapper.
    """

    success: bool = True
    data: T
    message: Optional[str] = None


class ErrorDetail(BaseSchema):
    """
    Standard error payload.
    """

    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseSchema):
    """
    Standard API error response wrapper.
    """

    success: bool = False
    error: ErrorDetail


class HealthStatus(BaseSchema):
    """
    Generic service/component health schema.
    """

    component: str
    status: str
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[dict] = None