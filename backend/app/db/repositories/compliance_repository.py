from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.compliance_audit import ComplianceAuditLog
from app.schemas.compliance import AuditLogEntry


class ComplianceRepository:
    """
    Database access layer for immutable compliance audit logs.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_audit_log(
        self,
        audit_entry: AuditLogEntry,
    ) -> ComplianceAuditLog:
        record = ComplianceAuditLog(
            log_id=audit_entry.log_id,
            workflow_run_id=audit_entry.workflow_run_id,
            agent_id=audit_entry.agent_id,
            agent_version=audit_entry.agent_version,
            execution_record_id=audit_entry.execution_record_id,
            input_hash=audit_entry.input_hash,
            sanctions_results=[
                item.model_dump(mode="json")
                for item in audit_entry.sanctions_results
            ],
            regulatory_results=[
                item.model_dump(mode="json")
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