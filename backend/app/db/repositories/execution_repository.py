from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.execution_record import ExecutionRecordModel
from app.db.models.rfq import RFQRecord
from app.schemas.execution import ExecutionRecord, RFQDocument


class ExecutionRepository:
    """
    Database access layer for RFQs and execution records.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_rfqs(
        self,
        rfqs: list[RFQDocument],
        mitigation_plan_id: str,
    ) -> list[RFQRecord]:
        records = []

        for rfq in rfqs:
            record = RFQRecord(
                mitigation_plan_id=mitigation_plan_id,
                rfq_id=rfq.rfq_id,
                supplier_id=rfq.supplier_id,
                supplier_name=rfq.supplier_name,
                supplier_email=rfq.supplier_email,
                line_items=[
                    item.model_dump(mode="json")
                    for item in rfq.line_items
                ],
                response_deadline=rfq.response_deadline,
                delivery_destination=rfq.delivery_destination,
                terms_ref=rfq.terms_ref,
                version=rfq.version,
                generated_by=rfq.generated_by,
                generated_at=rfq.generated_at,
            )

            self.session.add(record)
            records.append(record)

        await self.session.flush()

        for record in records:
            await self.session.refresh(record)

        return records

    async def save_execution_record(
        self,
        execution_record: ExecutionRecord,
        workflow_id: str | None = None,
    ) -> ExecutionRecordModel:
        record = ExecutionRecordModel(
            workflow_id=workflow_id,
            execution_id=execution_record.execution_id,
            mitigation_plan_id=execution_record.mitigation_plan_id,
            rfq_ids=[
                rfq.rfq_id
                for rfq in execution_record.rfqs
            ],
            approval_status=execution_record.approval_status,
            approval_decision_at=execution_record.approval_decision_at,
            approved_by=execution_record.approved_by,
            dispatch_log=[
                item.model_dump(mode="json")
                if hasattr(item, "model_dump")
                else item
                for item in execution_record.dispatch_log
            ],
            response_log=[
                item.model_dump(mode="json")
                if hasattr(item, "model_dump")
                else item
                for item in execution_record.response_log
            ],
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def get_execution_by_id(
        self,
        execution_id: str,
    ) -> ExecutionRecordModel | None:
        result = await self.session.execute(
            select(ExecutionRecordModel).where(
                ExecutionRecordModel.execution_id == execution_id
            )
        )

        return result.scalar_one_or_none()

    async def get_latest_for_plan(
        self,
        mitigation_plan_id: str,
    ) -> ExecutionRecordModel | None:
        result = await self.session.execute(
            select(ExecutionRecordModel)
            .where(
                ExecutionRecordModel.mitigation_plan_id
                == mitigation_plan_id
            )
            .order_by(desc(ExecutionRecordModel.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()