from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.base import Base

# Import models so Alembic can detect them
from app.db.models.supplier import Supplier  # noqa: F401
from app.db.models.risk_assessment import RiskAssessmentRecord  # noqa: F401
from app.db.models.mitigation_plan import MitigationPlanRecord  # noqa: F401
from app.db.models.rfq import RFQRecord  # noqa: F401
from app.db.models.risk_history import SupplierRiskHistory  # noqa: F401
from app.db.models.execution_record import ExecutionRecordModel  # noqa: F401
from app.db.models.compliance_audit import ComplianceAuditLog  # noqa: F401
from app.db.models.workflow_run import WorkflowRun  # noqa: F401
from app.db.models.workflow_event import WorkflowEvent  # noqa: F401
from app.db.models.active_order import ActiveOrder  # noqa: F401
from app.db.models.config import (  # noqa: F401
    RiskWeightConfig,
    MitigationWeightConfig,
    SystemConfig,
)


config = context.config

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """

    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(
    connection: Connection,
) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in online async mode.
    """

    configuration = config.get_section(
        config.config_ini_section,
        {},
    )

    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    Entry point for online migrations.
    """

    import asyncio

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
