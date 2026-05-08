from fastapi import APIRouter

from app.orchestration.workflow_runner import (
    run_supply_chain_workflow,
)


router = APIRouter(
    prefix="/workflow",
    tags=["Workflow"],
)


@router.post("/run/{supplier_id}")
async def run_workflow(
    supplier_id: str,
):
    """
    Run the complete LangGraph orchestration workflow.
    """

    state = await run_supply_chain_workflow(
        supplier_id=supplier_id,
        supplier_region="East Africa",
        risk_score_history=[
            20,
            21,
            19,
            22,
            20,
            21,
            20,
            19,
            22,
            21,
        ],
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
            state["compliance_verdict"].value
            if state.get("compliance_verdict")
            else None
        ),
        "workflow_complete": state.get(
            "workflow_complete",
            False,
        ),
    }