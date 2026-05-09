from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.compliance_audit import ComplianceAuditLog
from app.schemas.compliance import AuditLogEntry


class ComplianceRepository:
    """
    Database access layer for compliance audit logs.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_audit_log(
        self,
        audit_entry: AuditLogEntry,
        workflow_id: str | None = None,
    ) -> ComplianceAuditLog:
        record = ComplianceAuditLog(
            workflow_id=workflow_id,
            log_id=audit_entry.log_id,
            workflow_run_id=audit_entry.workflow_run_id,
            agent_id=audit_entry.agent_id,
            agent_version=audit_entry.agent_version,
            execution_record_id=audit_entry.execution_record_id,
            input_hash=audit_entry.input_hash,
            sanctions_results=[
                item.model_dump(mode="json")
                if hasattr(item, "model_dump")
                else item
                for item in audit_entry.sanctions_results
            ],
            regulatory_results=[
                item.model_dump(mode="json")
                if hasattr(item, "model_dump")
                else item
                for item in audit_entry.regulatory_results
            ],
            verdict=audit_entry.verdict,
            verdict_rationale=audit_entry.verdict_rationale,
            llm_summary=audit_entry.llm_summary,
            created_at=audit_entry.created_at,
        )

        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)

        return record

    async def get_by_log_id(
        self,
        log_id: str,
    ) -> ComplianceAuditLog | None:
        result = await self.session.execute(
            select(ComplianceAuditLog).where(
                ComplianceAuditLog.log_id == log_id
            )
        )

        return result.scalar_one_or_none()

    async def get_latest_for_execution(
        self,
        execution_record_id: str,
    ) -> ComplianceAuditLog | None:
        result = await self.session.execute(
            select(ComplianceAuditLog)
            .where(
                ComplianceAuditLog.execution_record_id
                == execution_record_id
            )
            .order_by(desc(ComplianceAuditLog.created_at))
            .limit(1)
        )

        return result.scalar_one_or_none()