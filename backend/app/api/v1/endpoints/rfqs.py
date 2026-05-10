from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rfq import RFQActionHistory, RFQRecord
from app.db.session import get_db_session
from app.schemas.rfqs import (
    RFQActionRequest,
    RFQActionsResponse,
    RFQActionHistoryResponse,
    RFQDetailResponse,
    RFQListResponse,
    RFQResponse,
)
from app.services.rfq_service import RFQService

router = APIRouter(
    prefix="/rfqs",
    tags=["RFQs"],
)


@router.get("", response_model=RFQListResponse)
async def list_rfqs(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)

    try:
        rfqs, total = await service.list_rfqs(
            search=search,
            status=status,
            limit=limit,
            offset=offset,
        )
    except KeyError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported RFQ status: {status}",
        ) from exc

    return RFQListResponse(
        count=len(rfqs),
        total=total,
        limit=limit,
        offset=offset,
        rfqs=[_rfq_to_response(rfq) for rfq in rfqs],
    )


@router.get("/{rfq_id}", response_model=RFQDetailResponse)
async def get_rfq(
    rfq_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)
    rfq = await service.get_rfq(rfq_id)

    if rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return RFQDetailResponse(rfq=_rfq_to_response(rfq))


@router.post("/{rfq_id}/approve", response_model=RFQDetailResponse)
async def approve_rfq(
    rfq_id: str,
    request: RFQActionRequest | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)
    payload = request or RFQActionRequest()
    rfq = await service.approve(
        rfq_id=rfq_id,
        actor=payload.actor or "procurement_user",
        note=payload.note,
    )

    if rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return RFQDetailResponse(rfq=_rfq_to_response(rfq))


@router.post("/{rfq_id}/request-review", response_model=RFQDetailResponse)
async def request_rfq_review(
    rfq_id: str,
    request: RFQActionRequest | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)
    payload = request or RFQActionRequest()
    rfq = await service.request_review(
        rfq_id=rfq_id,
        actor=payload.actor or "procurement_user",
        note=payload.note,
    )

    if rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return RFQDetailResponse(rfq=_rfq_to_response(rfq))


@router.post("/{rfq_id}/reject", response_model=RFQDetailResponse)
async def reject_rfq(
    rfq_id: str,
    request: RFQActionRequest | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)
    payload = request or RFQActionRequest()
    rfq = await service.reject(
        rfq_id=rfq_id,
        actor=payload.actor or "procurement_user",
        note=payload.note,
    )

    if rfq is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return RFQDetailResponse(rfq=_rfq_to_response(rfq))


@router.get("/{rfq_id}/actions", response_model=RFQActionsResponse)
async def list_rfq_actions(
    rfq_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    service = RFQService(session)
    actions = await service.list_actions(rfq_id)

    if actions is None:
        raise HTTPException(status_code=404, detail="RFQ not found")

    return RFQActionsResponse(
        count=len(actions),
        actions=[_action_to_response(action) for action in actions],
    )


def _rfq_to_response(rfq: RFQRecord) -> RFQResponse:
    return RFQResponse(
        id=rfq.id,
        rfq_id=rfq.rfq_id,
        mitigation_plan_id=rfq.mitigation_plan_id,
        workflow_id=rfq.workflow_id,
        supplier_id=rfq.supplier_id,
        supplier_name=rfq.supplier_name,
        supplier_code=rfq.supplier_code or rfq.supplier_id,
        supplier_email=rfq.supplier_email,
        line_items=rfq.line_items,
        response_deadline=rfq.response_deadline,
        delivery_destination=rfq.delivery_destination,
        terms_ref=rfq.terms_ref,
        status=rfq.status,
        price=rfq.price,
        currency=rfq.currency,
        lead_time_days=rfq.lead_time_days,
        risk_summary=rfq.risk_summary,
        notes=rfq.notes,
        version=rfq.version,
        generated_by=rfq.generated_by,
        generated_at=rfq.generated_at,
        created_at=rfq.created_at,
        updated_at=rfq.updated_at,
    )


def _action_to_response(action: RFQActionHistory) -> RFQActionHistoryResponse:
    return RFQActionHistoryResponse(
        id=action.id,
        rfq_record_id=action.rfq_record_id,
        rfq_id=action.rfq_id,
        action_type=action.action_type,
        previous_status=action.previous_status,
        new_status=action.new_status,
        actor=action.actor,
        note=action.note,
        created_at=action.created_at,
    )