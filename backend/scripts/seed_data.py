import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import delete

from app.db.models.active_order import ActiveOrder
from app.db.models.compliance_audit import ComplianceAuditLog
from app.db.models.config import (
    MitigationWeightConfig,
    RiskWeightConfig,
    SystemConfig,
)
from app.db.models.execution_record import ExecutionRecordModel
from app.db.models.mitigation_plan import MitigationPlanRecord
from app.db.models.rfq import RFQActionHistory, RFQRecord
from app.db.models.risk_assessment import RiskAssessmentRecord
from app.db.models.risk_history import SupplierRiskHistory
from app.db.models.supplier import Supplier
from app.db.models.workflow_event import WorkflowEvent
from app.db.models.workflow_run import WorkflowRun
from app.db.session import AsyncSessionLocal
from app.schemas.assessments import RiskLevel
from app.schemas.compliance import ComplianceVerdict
from app.schemas.execution import ApprovalStatus, RFQStatus
from app.schemas.suppliers import (
    ComplianceStatus,
    RelationshipStatus,
    SupplierStatus,
)


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"
NOW = datetime(2026, 5, 10, 8, 0, tzinfo=UTC)


EXTRA_SUPPLIERS = [
    {
        "id": "SUP-SE-001",
        "name": "Nordic Freight Systems",
        "country": "Sweden",
        "region": "Europe",
        "contact_email": "ops@nordicfreight.example",
        "product_categories": ["logistics", "freight", "cold_chain"],
        "certifications": ["ISO9001", "GDP"],
        "status": "active",
        "compliance_status": "approved",
        "relationship_status": "active_secondary",
        "unit_cost": 7.4,
        "typical_lead_time_days": 9,
        "capacity_units_per_month": 55000,
        "on_time_delivery_rate": 0.96,
        "quality_score": 92,
        "latest_risk_score": 19,
        "supplier_profile_text": "Low-risk European logistics partner with strong cold-chain and freight reliability.",
    },
    {
        "id": "SUP-EG-001",
        "name": "Nile Agro Exports",
        "country": "Egypt",
        "region": "Middle East",
        "contact_email": "exports@nileagro.example",
        "product_categories": ["agriculture", "food_inputs", "packaging"],
        "certifications": ["ISO9001", "GLOBALGAP"],
        "status": "active",
        "compliance_status": "approved",
        "relationship_status": "new",
        "unit_cost": 6.8,
        "typical_lead_time_days": 24,
        "capacity_units_per_month": 74000,
        "on_time_delivery_rate": 0.82,
        "quality_score": 81,
        "latest_risk_score": 47,
        "supplier_profile_text": "Agriculture supplier exposed to weather disruption and Suez-region logistics volatility.",
    },
    {
        "id": "SUP-SG-001",
        "name": "Vertex Industrial Plastics",
        "country": "Singapore",
        "region": "Southeast Asia",
        "contact_email": "rfq@vertexplastics.example",
        "product_categories": ["industrial_components", "plastics", "automotive"],
        "certifications": ["ISO9001", "IATF16949"],
        "status": "active",
        "compliance_status": "approved",
        "relationship_status": "active_secondary",
        "unit_cost": 9.1,
        "typical_lead_time_days": 17,
        "capacity_units_per_month": 62000,
        "on_time_delivery_rate": 0.91,
        "quality_score": 90,
        "latest_risk_score": 31,
        "supplier_profile_text": "Automotive plastics supplier with moderate logistics exposure and strong quality controls.",
    },
    {
        "id": "SUP-AE-001",
        "name": "Atlas Logistics Group",
        "country": "United Arab Emirates",
        "region": "Middle East",
        "contact_email": "controltower@atlaslogistics.example",
        "product_categories": ["logistics", "freight", "energy"],
        "certifications": ["ISO9001", "TAPA"],
        "status": "active",
        "compliance_status": "approved",
        "relationship_status": "active_secondary",
        "unit_cost": 8.9,
        "typical_lead_time_days": 11,
        "capacity_units_per_month": 88000,
        "on_time_delivery_rate": 0.89,
        "quality_score": 87,
        "latest_risk_score": 39,
        "supplier_profile_text": "Regional logistics group affected by Red Sea route disruption and fuel-price volatility.",
    },
    {
        "id": "SUP-UK-001",
        "name": "EastBridge Medical Supply",
        "country": "United Kingdom",
        "region": "Europe",
        "contact_email": "medical@eastbridge.example",
        "product_categories": ["pharma", "medical_devices", "packaging"],
        "certifications": ["ISO13485", "GMP"],
        "status": "active",
        "compliance_status": "approved",
        "relationship_status": "new",
        "unit_cost": 14.2,
        "typical_lead_time_days": 12,
        "capacity_units_per_month": 26000,
        "on_time_delivery_rate": 0.94,
        "quality_score": 95,
        "latest_risk_score": 22,
        "supplier_profile_text": "Medical supply provider with strong compliance posture and limited monthly capacity.",
    },
]


def load_json(filename: str):
    with open(SEED_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


async def clear_existing_data() -> None:
    """
    Remove old demo seed data.

    Risk history must be deleted before suppliers because it has
    a foreign key to suppliers.
    """

    async with AsyncSessionLocal() as session:
        await session.execute(delete(RFQActionHistory))
        await session.execute(delete(RFQRecord))
        await session.execute(delete(ExecutionRecordModel))
        await session.execute(delete(ComplianceAuditLog))
        await session.execute(delete(MitigationPlanRecord))
        await session.execute(delete(RiskAssessmentRecord))
        await session.execute(delete(WorkflowEvent))
        await session.execute(delete(WorkflowRun))
        await session.execute(delete(ActiveOrder))
        await session.execute(delete(SupplierRiskHistory))
        await session.execute(delete(Supplier))
        await session.execute(delete(RiskWeightConfig))
        await session.execute(delete(MitigationWeightConfig))
        await session.execute(delete(SystemConfig))

        await session.commit()

    print("Old seed data cleared.")


async def seed_suppliers() -> None:
    suppliers = load_json("suppliers.json")
    suppliers.extend(EXTRA_SUPPLIERS)

    async with AsyncSessionLocal() as session:
        for supplier in suppliers:
            supplier["status"] = SupplierStatus(supplier["status"])
            supplier["compliance_status"] = ComplianceStatus(
                supplier["compliance_status"]
            )
            supplier["relationship_status"] = RelationshipStatus(
                supplier["relationship_status"]
            )
            session.add(Supplier(**supplier))

        await session.commit()

    print(f"Suppliers inserted: {len(suppliers)}")


async def seed_active_orders() -> None:
    orders = load_json("orders.json")

    async with AsyncSessionLocal() as session:
        for index, order in enumerate(orders[:8], start=1):
            session.add(
                ActiveOrder(
                    id=f"ORD-SEED-{index:03d}",
                    supplier_id=order["supplier_id"],
                    supplier_name=order["supplier_name"],
                    destination_country=order.get("destination_country", "United States"),
                    destination=order.get("destination", "Chicago DC"),
                    volume_units=order.get("volume_units", 15000),
                    risk_level=order.get("risk_level", "MEDIUM"),
                    line_items=order.get(
                        "line_items",
                        [
                            {
                                "sku": f"SKU-SEED-{index:03d}",
                                "description": "Seeded production component",
                                "quantity": 1000 + index * 250,
                                "unit": "units",
                            }
                        ],
                    ),
                    status="ACTIVE",
                    created_at=NOW - timedelta(days=index),
                )
            )

        await session.commit()

    print("Active orders inserted: 8")


async def seed_workflows_and_rfqs() -> None:
    supplier_refs = [
        ("SUP-CN-001", "Pacific Semiconductor Labs", RiskLevel.HIGH, 68.0),
        ("SUP-DE-001", "EuroTech Components", RiskLevel.LOW, 18.0),
        ("SUP-IN-001", "Apex India Manufacturing", RiskLevel.MEDIUM, 36.0),
        ("SUP-SE-001", "Nordic Freight Systems", RiskLevel.LOW, 19.0),
        ("SUP-EG-001", "Nile Agro Exports", RiskLevel.MEDIUM, 47.0),
        ("SUP-AE-001", "Atlas Logistics Group", RiskLevel.HIGH, 64.0),
        ("SUP-SG-001", "Vertex Industrial Plastics", RiskLevel.MEDIUM, 31.0),
        ("SUP-UK-001", "EastBridge Medical Supply", RiskLevel.LOW, 22.0),
        ("SUP-IR-001", "TerraFuel Energy", RiskLevel.CRITICAL, 95.0),
        ("SUP-RU-001", "Northern Metals Export", RiskLevel.HIGH, 70.0),
        ("SUP-US-001", "Quantum Circuit Manufacturing", RiskLevel.LOW, 22.0),
        ("SUP-JP-001", "Kyoto Advanced Circuits", RiskLevel.LOW, 24.0),
    ]
    workflow_statuses = [
        "completed",
        "completed",
        "completed_without_mitigation",
        "failed",
        "pending",
        "completed",
        "completed_without_execution",
        "completed_without_audit",
        "completed",
        "failed",
        "completed",
        "pending",
    ]
    rfq_statuses = [
        RFQStatus.DRAFT,
        RFQStatus.PENDING_APPROVAL,
        RFQStatus.PENDING_APPROVAL,
        RFQStatus.PENDING_APPROVAL,
        RFQStatus.APPROVED,
        RFQStatus.APPROVED,
        RFQStatus.REJECTED,
        RFQStatus.REVIEW_REQUESTED,
        RFQStatus.COMPLIANCE_REVIEW,
    ]

    async with AsyncSessionLocal() as session:
        for index, (supplier_id, supplier_name, risk_level, score) in enumerate(
            supplier_refs,
            start=1,
        ):
            workflow_id = f"WF-SEED-{index:03d}"
            started_at = NOW - timedelta(days=index, hours=index)
            completed_at = (
                started_at + timedelta(minutes=18 + index)
                if workflow_statuses[index - 1] not in {"pending", "running"}
                else None
            )

            session.add(
                WorkflowRun(
                    id=f"WR-SEED-{index:03d}",
                    workflow_id=workflow_id,
                    supplier_id=supplier_id,
                    workflow_status=workflow_statuses[index - 1],
                    correlation_id=f"CORR-SEED-{index:03d}",
                    started_at=started_at,
                    completed_at=completed_at,
                    error_message=(
                        "Supplier signal fetch timed out during logistics enrichment"
                        if workflow_statuses[index - 1] == "failed"
                        else None
                    ),
                    final_state_snapshot={
                        "supplier_id": supplier_id,
                        "supplier_name": supplier_name,
                        "risk_level": risk_level.value,
                    },
                    created_at=started_at,
                    updated_at=completed_at,
                )
            )
            session.add(
                RiskAssessmentRecord(
                    id=f"RISK-SEED-{index:03d}",
                    workflow_id=workflow_id,
                    supplier_id=supplier_id,
                    score=score,
                    level=risk_level,
                    factor_breakdown={
                        "financial": min(score + 4, 100),
                        "geopolitical": min(score + index, 100),
                        "logistics": min(score + 8, 100),
                        "weather": max(score - 6, 0),
                        "tariff": max(score - 12, 0),
                    },
                    contributing_signals=[
                        "financial",
                        "geopolitical",
                        "logistics",
                        "weather",
                    ],
                    anomaly_detected=risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL},
                    anomaly_direction="spike" if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} else None,
                    anomaly_z_score=2.4 if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL} else None,
                    anomaly_baseline_mean=max(score - 14, 0),
                    anomaly_data={
                        "reason": "Seeded disruption signal for full-system validation",
                    },
                    reasoning_summary=(
                        f"{supplier_name} risk is {risk_level.value.lower()} due to current "
                        "financial, logistics, weather, and geopolitical signals."
                    ),
                    assessed_at=started_at + timedelta(minutes=3),
                    created_at=started_at + timedelta(minutes=3),
                )
            )

            mitigation_id = f"MIT-SEED-{index:03d}"
            has_mitigation = workflow_statuses[index - 1] != "completed_without_mitigation"
            if has_mitigation:
                session.add(
                    MitigationPlanRecord(
                        id=mitigation_id,
                        workflow_id=workflow_id,
                        original_supplier_id=supplier_id,
                        risk_score=score,
                        recommended_options=[
                            {
                                "option_id": f"OPT-SEED-{index:03d}-A",
                                "supplier_id": "SUP-DE-001",
                                "supplier_name": "EuroTech Components",
                                "description": "Shift urgent component allocation to a lower-risk European supplier.",
                                "rank": 1,
                                "cost_delta_pct": 8.5,
                                "lead_time_delta_days": -4,
                                "residual_risk_score": 22.0,
                                "onboarding_weeks": 1,
                                "confidence": 0.86,
                                "cost_estimate": 118000 + index * 2100,
                            },
                            {
                                "option_id": f"OPT-SEED-{index:03d}-B",
                                "supplier_id": "SUP-IN-001",
                                "supplier_name": "Apex India Manufacturing",
                                "description": "Use approved secondary capacity while monitoring port delays.",
                                "rank": 2,
                                "cost_delta_pct": 3.2,
                                "lead_time_delta_days": 2,
                                "residual_risk_score": 34.0,
                                "onboarding_weeks": 2,
                                "confidence": 0.74,
                                "cost_estimate": 104000 + index * 1800,
                            },
                        ],
                        candidate_suppliers=[
                            {"id": "SUP-DE-001", "name": "EuroTech Components"},
                            {"id": "SUP-IN-001", "name": "Apex India Manufacturing"},
                            {"id": "SUP-SE-001", "name": "Nordic Freight Systems"},
                        ],
                        simulated_scenarios=[
                            {
                                "scenario": "split_sourcing",
                                "risk_reduction": 31,
                                "service_impact": "Inventory cover restored within 6 days",
                            }
                        ],
                        justification="Seeded mitigation plan for realistic workflow validation.",
                        created_by_agent="mitigation_strategist",
                        created_at=started_at + timedelta(minutes=7),
                    )
                )
                await session.flush()

                session.add(
                    ExecutionRecordModel(
                        id=f"EXECREC-SEED-{index:03d}",
                        workflow_id=workflow_id,
                        execution_id=f"EXEC-SEED-{index:03d}",
                        mitigation_plan_id=mitigation_id,
                        rfq_ids=[f"RFQ-SEED-{index:03d}-{suffix}" for suffix in ("A", "B", "C")],
                        approval_status=(
                            ApprovalStatus.PENDING_HUMAN
                            if risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
                            else ApprovalStatus.AUTO_APPROVED
                        ),
                        approval_decision_at=None,
                        approved_by=None,
                        dispatch_log=[],
                        response_log=[],
                        created_by_agent="execution_agent",
                        created_at=started_at + timedelta(minutes=11),
                    )
                )

                verdict = (
                    ComplianceVerdict.BLOCKED
                    if risk_level == RiskLevel.CRITICAL
                    else ComplianceVerdict.FLAGGED
                    if risk_level == RiskLevel.HIGH
                    else ComplianceVerdict.CLEARED
                )
                session.add(
                    ComplianceAuditLog(
                        id=f"COMP-SEED-{index:03d}",
                        workflow_id=workflow_id,
                        log_id=f"LOG-SEED-{index:03d}",
                        workflow_run_id=workflow_id,
                        agent_id="compliance_agent",
                        agent_version="seed-1.0",
                        execution_record_id=f"EXEC-SEED-{index:03d}",
                        input_hash=f"seed-hash-{index:03d}",
                        sanctions_results=[],
                        regulatory_results=[
                            {
                                "check_type": "trade_restriction",
                                "passed": verdict == ComplianceVerdict.CLEARED,
                                "details": "Seeded compliance result for demo review.",
                                "applicable_regulation": "Internal sourcing policy",
                            }
                        ],
                        verdict=verdict,
                        verdict_rationale="Seeded compliance case for validation.",
                        llm_summary=f"{supplier_name} compliance result: {verdict.value}.",
                        created_by_agent="compliance_agent",
                        created_at=started_at + timedelta(minutes=14),
                    )
                )

            for event_index, event_type in enumerate(
                ["risk_assessed", "mitigation_planned", "rfq_prepared", "compliance_checked"],
                start=1,
            ):
                session.add(
                    WorkflowEvent(
                        id=f"EVT-SEED-{index:03d}-{event_index}",
                        workflow_id=workflow_id,
                        supplier_id=supplier_id,
                        event_type=event_type,
                        agent_name=event_type.split("_")[0],
                        status="completed" if workflow_statuses[index - 1] != "failed" else "failed",
                        message=f"{event_type.replace('_', ' ').title()} for {supplier_name}",
                        payload={"supplier_name": supplier_name},
                        error_message=(
                            "Seeded workflow failure event"
                            if workflow_statuses[index - 1] == "failed" and event_index == 2
                            else None
                        ),
                        created_at=started_at + timedelta(minutes=event_index * 3),
                    )
                )

        rfq_suppliers = [
            ("SUP-DE-001", "EuroTech Components", "electronics"),
            ("SUP-IN-001", "Apex India Manufacturing", "electronics"),
            ("SUP-SE-001", "Nordic Freight Systems", "logistics"),
            ("SUP-EG-001", "Nile Agro Exports", "agriculture"),
            ("SUP-AE-001", "Atlas Logistics Group", "logistics"),
            ("SUP-SG-001", "Vertex Industrial Plastics", "automotive"),
            ("SUP-UK-001", "EastBridge Medical Supply", "pharma"),
            ("SUP-US-001", "Quantum Circuit Manufacturing", "semiconductor manufacturing"),
            ("SUP-JP-001", "Kyoto Advanced Circuits", "semiconductor manufacturing"),
        ]
        workflow_indexes_with_mitigation = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        for rfq_index in range(1, 46):
            supplier_id, supplier_name, industry = rfq_suppliers[(rfq_index - 1) % len(rfq_suppliers)]
            workflow_index = workflow_indexes_with_mitigation[
                (rfq_index - 1) % len(workflow_indexes_with_mitigation)
            ]
            status = rfq_statuses[(rfq_index - 1) % len(rfq_statuses)]
            created_at = NOW - timedelta(hours=rfq_index * 3)
            rfq_id = f"RFQ-SEED-{rfq_index:03d}"
            price = 74000 + rfq_index * 2750
            lead_time = 7 + (rfq_index % 24)

            session.add(
                RFQRecord(
                    id=f"RFQREC-SEED-{rfq_index:03d}",
                    mitigation_plan_id=f"MIT-SEED-{workflow_index:03d}",
                    rfq_id=rfq_id,
                    workflow_id=f"WF-SEED-{workflow_index:03d}",
                    supplier_id=supplier_id,
                    supplier_name=supplier_name,
                    supplier_code=supplier_id,
                    supplier_email=f"rfq-{supplier_id.lower()}@example.test",
                    line_items=[
                        {
                            "sku": f"SKU-{industry[:3].upper()}-{rfq_index:03d}",
                            "description": f"{industry.title()} replenishment component with long text rendering validation",
                            "quantity": 800 + rfq_index * 25,
                            "unit": "units",
                            "target_price": price,
                            "notes": "Seeded RFQ line item for end-to-end validation.",
                        }
                    ],
                    response_deadline=created_at + timedelta(days=5 + (rfq_index % 8)),
                    delivery_destination="Chicago Consolidation Center",
                    terms_ref="NET30-FOB-SEED",
                    status=status,
                    price=price,
                    currency="USD",
                    lead_time_days=lead_time,
                    risk_summary=(
                        "Low residual risk"
                        if status == RFQStatus.APPROVED
                        else "Compliance review required"
                        if status == RFQStatus.COMPLIANCE_REVIEW
                        else "Monitor logistics, finance, and weather signals"
                    ),
                    notes=(
                        "Seeded long review note: supplier has stable capacity, but procurement should confirm "
                        "allocation windows, currency exposure, and downstream production timing before final award."
                        if rfq_index % 10 == 0
                        else "Seeded backend RFQ record."
                    ),
                    version=1,
                    generated_by="seed_data",
                    generated_at=created_at,
                    created_at=created_at,
                    updated_at=created_at + timedelta(hours=1),
                )
            )
            await session.flush()

            if status not in {RFQStatus.DRAFT, RFQStatus.PENDING_APPROVAL}:
                action_type = {
                    RFQStatus.APPROVED: "APPROVE",
                    RFQStatus.REJECTED: "REJECT",
                    RFQStatus.REVIEW_REQUESTED: "REQUEST_REVIEW",
                    RFQStatus.COMPLIANCE_REVIEW: "REQUEST_REVIEW",
                }[status]
                session.add(
                    RFQActionHistory(
                        id=f"RFQACT-SEED-{rfq_index:03d}",
                        rfq_record_id=f"RFQREC-SEED-{rfq_index:03d}",
                        rfq_id=rfq_id,
                        action_type=action_type,
                        previous_status=RFQStatus.PENDING_APPROVAL.name,
                        new_status=status.name,
                        actor="seed_procurement_user",
                        note=f"Seeded {status.value.lower().replace('_', ' ')} action.",
                        created_at=created_at + timedelta(hours=1),
                    )
                )

        await session.commit()

    print("Workflow runs inserted: 12")
    print("RFQs inserted: 45")
    print("RFQ action history records inserted: 25")


async def seed_risk_history() -> None:
    history_data = load_json("risk_history.json")

    async with AsyncSessionLocal() as session:
        total = 0

        for item in history_data:
            supplier_id = item["supplier_id"]

            for score in item["scores"]:
                session.add(
                    SupplierRiskHistory(
                        supplier_id=supplier_id,
                        risk_score=score,
                    )
                )
                total += 1

        await session.commit()

    print(f"Risk history records inserted: {total}")


async def seed_risk_weights() -> None:
    data = load_json("risk_weights.json")

    async with AsyncSessionLocal() as session:
        record = RiskWeightConfig(
            financial_weight=data["financial_weight"],
            geopolitical_weight=data["geopolitical_weight"],
            logistics_weight=data["logistics_weight"],
            weather_weight=data["weather_weight"],
            tariff_weight=data["tariff_weight"],
            is_active=True,
        )

        session.add(record)
        await session.commit()

    print("Risk weight config inserted.")


async def seed_mitigation_weights() -> None:
    data = load_json("mitigation_weights.json")

    async with AsyncSessionLocal() as session:
        record = MitigationWeightConfig(
            cost_delta_weight=data["cost_delta_weight"],
            lead_time_weight=data["lead_time_weight"],
            residual_risk_weight=data["residual_risk_weight"],
            onboarding_weight=data["onboarding_weight"],
            confidence_weight=data["confidence_weight"],
            is_active=True,
        )

        session.add(record)
        await session.commit()

    print("Mitigation weight config inserted.")


async def seed_system_configs() -> None:
    configs = [
        {
            "config_key": "default_currency",
            "config_value": {"value": "USD"},
            "description": "Default currency for simulation pricing",
        },
        {
            "config_key": "default_destination_region",
            "config_value": {"value": "East Africa"},
            "description": "Default destination region for demo workflows",
        },
        {
            "config_key": "workflow_mode",
            "config_value": {"value": "simulation"},
            "description": "Current workflow execution mode",
        },
        {
            "config_key": "seed_dataset_version",
            "config_value": {"value": "stage_11_curated_v1"},
            "description": "Version of curated demo dataset",
        },
    ]

    async with AsyncSessionLocal() as session:
        for item in configs:
            session.add(SystemConfig(**item))

        await session.commit()

    print(f"System configs inserted: {len(configs)}")


async def main() -> None:
    print("Starting SupplyChain Guardian seed process...")

    await clear_existing_data()

    await seed_suppliers()
    await seed_active_orders()
    await seed_risk_history()
    await seed_workflows_and_rfqs()
    await seed_risk_weights()
    await seed_mitigation_weights()
    await seed_system_configs()

    print("\nSeed complete.")
    print("Demo scenarios ready:")
    print("- SUP-CN-001 → HIGH risk + anomaly")
    print("- SUP-DE-001 → CLEARED compliance path")
    print("- SUP-IN-001 → FLAGGED GDPR path")
    print("- SUP-IR-001 → BLOCKED sanctions path")


if __name__ == "__main__":
    asyncio.run(main())
