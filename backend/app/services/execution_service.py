import asyncio
from uuid import uuid4

from app.engine.approval_router import (
    pre_execution_gate,
    route_approval,
)
from app.engine.dispatcher import dispatch_rfq
from app.engine.rfq_generator import generate_rfq
from app.notifications.slack import (
    build_approval_slack_message,
    post_approval_request,
)
from app.schemas.execution import (
    ApprovalStatus,
    ExecutionRecord,
)
from app.schemas.mitigation import MitigationPlan
from app.services.mitigation_service import mitigation_service


class ExecutionService:
    """
    Coordinates RFQ generation, approval routing,
    and dispatch workflows.
    """

    async def generate_execution_record(
        self,
        mitigation_plan: MitigationPlan,
    ) -> ExecutionRecord:
        """
        Main execution workflow.
        """

        gate_result = pre_execution_gate(mitigation_plan)

        suppliers = await asyncio.gather(
            *[
                mitigation_service.get_alternative_suppliers(
                    {"id": mitigation_plan.original_supplier_id}
                )
            ]
        )

        supplier_lookup = {
            supplier["id"]: supplier
            for supplier in suppliers[0]
        }

        current_order = await mitigation_service.get_active_order(
            mitigation_plan.original_supplier_id
        )

        rfqs = []

        for option in mitigation_plan.recommended_options:
            supplier = supplier_lookup[option.supplier_id]

            rfq = generate_rfq(
                option=option.model_dump(mode="json"),
                supplier=supplier,
                original_order=current_order,
                plan_id=mitigation_plan.id or str(uuid4()),
            )

            rfqs.append(rfq)

        approval_status = await route_approval(
            rfqs=rfqs,
            gate_result=gate_result,
            mitigation_plan=mitigation_plan,
        )

        dispatch_log = []

        if approval_status == ApprovalStatus.AUTO_APPROVED:
            dispatch_log = await asyncio.gather(
                *[
                    dispatch_rfq(
                        rfq,
                        simulated=True,
                    )
                    for rfq in rfqs
                ]
            )

        elif approval_status == ApprovalStatus.PENDING_HUMAN:
            slack_message = build_approval_slack_message(
                rfqs=rfqs,
                gate_result=gate_result,
                mitigation_plan=mitigation_plan,
            )

            await post_approval_request(
                channel="#procurement-approvals",
                message=slack_message,
            )

        return ExecutionRecord(
            execution_id=str(uuid4()),
            mitigation_plan_id=mitigation_plan.id or "MVP-PLAN",
            rfqs=rfqs,
            approval_status=approval_status,
            approval_decision_at=None,
            approved_by=(
                "auto"
                if approval_status == ApprovalStatus.AUTO_APPROVED
                else None
            ),
            dispatch_log=dispatch_log,
            response_log=[],
        )


execution_service = ExecutionService()