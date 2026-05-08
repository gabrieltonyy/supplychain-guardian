from fastapi import APIRouter

from app.orchestration.db_workflow_runner import (
    run_db_supply_chain_workflow,
)


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

    state = await run_db_supply_chain_workflow(
        supplier_id=supplier_id,
    )

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
        "compliance_verdict": (
            state.get("compliance_verdict").value
            if state.get("compliance_verdict")
            else None
        ),
        "workflow_complete": state.get(
            "workflow_complete",
            False,
        ),
    }