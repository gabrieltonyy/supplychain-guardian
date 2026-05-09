from fastapi import APIRouter
from fastapi import HTTPException, Query

from app.db.session import AsyncSessionLocal
from app.orchestration.db_workflow_runner import (
    run_db_supply_chain_workflow,
)
from app.services.workflow_analytics_service import (
    WorkflowAnalyticsService,
)
from app.services.workflow_query_service import WorkflowQueryService


router = APIRouter(
    prefix="/api/v1/db-workflow",
    tags=["DB Workflow"],
)


@router.post("/run/{supplier_id}")
async def run_workflow(
    supplier_id: str,
):
    """
    Run database-backed supply chain workflow.
    """

    try:
        state = await run_db_supply_chain_workflow(
            supplier_id=supplier_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "supplier_id": supplier_id,
                "error_type": "workflow_validation_error",
                "message": str(exc),
            },
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "supplier_id": supplier_id,
                "error_type": "workflow_execution_error",
                "message": str(exc),
            },
        ) from exc

    return {
        "success": True,
        "workflow_id": state.get("workflow_id"),
        "workflow_status": state.get("workflow_status"),
        "supplier_id": supplier_id,
        "risk_assessment": (
            state["risk_assessment"].model_dump(mode="json")
            if state.get("risk_assessment")
            else None
        ),
        "anomaly_detection": (
            state["anomaly_detection"].model_dump(mode="json")
            if state.get("anomaly_detection")
            else None
        ),
        "reasoning_summary": state.get("reasoning_summary"),
        "ai_reasoning_source": state.get(
            "ai_reasoning_source",
        ),
        "mitigation_reasoning_summary": state.get(
            "mitigation_reasoning_summary",
        ),
        "mitigation_reasoning_source": state.get(
            "mitigation_reasoning_source",
        ),
        "mitigation_plan": (
            state["mitigation_plan"].model_dump(mode="json")
            if state.get("mitigation_plan")
            else None
        ),
        "execution_record": (
            state["execution_record"].model_dump(mode="json")
            if state.get("execution_record")
            else None
        ),
        "execution_reasoning_summary": state.get(
            "execution_reasoning_summary",
        ),
        "execution_reasoning_source": state.get(
            "execution_reasoning_source",
        ),
        "compliance_verdict": (
            state.get("compliance_verdict").value
            if state.get("compliance_verdict")
            else None
        ),
        "compliance_reasoning_summary": state.get(
            "compliance_reasoning_summary",
        ),
        "compliance_reasoning_source": state.get(
            "compliance_reasoning_source",
        ),
        "workflow_complete": state.get(
            "workflow_complete",
            False,
        ),
    }


@router.get("/runs")
async def list_workflow_runs(
    limit: int = Query(default=50, ge=1, le=200),
):
    async with AsyncSessionLocal() as session:
        service = WorkflowQueryService(session)
        runs = await service.list_runs(limit=limit)

    return {
        "success": True,
        "count": len(runs),
        "runs": [
            service._model_to_dict(run)
            for run in runs
        ],
    }


@router.get("/{workflow_id}")
async def get_workflow_run(
    workflow_id: str,
):
    async with AsyncSessionLocal() as session:
        service = WorkflowQueryService(session)
        run = await service.get_run(workflow_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found",
        )

    return {
        "success": True,
        "workflow_run": service._model_to_dict(run),
    }


@router.get("/{workflow_id}/timeline")
async def get_workflow_timeline(
    workflow_id: str,
):
    async with AsyncSessionLocal() as session:
        service = WorkflowQueryService(session)
        run = await service.get_run(workflow_id)

        if run is None:
            raise HTTPException(
                status_code=404,
                detail="Workflow run not found",
            )

        timeline = await service.get_timeline(workflow_id)

    return {
        "success": True,
        "workflow_id": workflow_id,
        "count": len(timeline),
        "timeline": [
            service._model_to_dict(event)
            for event in timeline
        ],
    }


@router.get("/{workflow_id}/replay")
async def replay_workflow(
    workflow_id: str,
):
    async with AsyncSessionLocal() as session:
        service = WorkflowQueryService(session)
        replay = await service.get_replay(workflow_id)

    if replay is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found",
        )

    return {
        "success": True,
        "workflow_id": workflow_id,
        "replay": replay,
    }


@router.get("/analytics/summary")
async def workflow_summary():
    async with AsyncSessionLocal() as session:
        service = WorkflowAnalyticsService(session)
        summary = await service.workflow_summary()

    return {
        "success": True,
        "summary": summary,
    }


@router.get("/analytics/risk-distribution")
async def risk_distribution():
    async with AsyncSessionLocal() as session:
        service = WorkflowAnalyticsService(session)
        distribution = await service.risk_distribution()

    return {
        "success": True,
        "distribution": distribution,
    }


@router.get("/analytics/supplier-rankings")
async def supplier_rankings(
    limit: int = Query(default=10, ge=1, le=100),
):
    async with AsyncSessionLocal() as session:
        service = WorkflowAnalyticsService(session)
        rankings = await service.supplier_risk_rankings(limit)

    return {
        "success": True,
        "rankings": rankings,
    }