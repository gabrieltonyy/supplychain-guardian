import asyncio
import json
from pathlib import Path

from sqlalchemy import delete

from app.db.models.config import (
    MitigationWeightConfig,
    RiskWeightConfig,
    SystemConfig,
)
from app.db.models.risk_history import SupplierRiskHistory
from app.db.models.supplier import Supplier
from app.db.session import AsyncSessionLocal


BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
SEED_DIR = PROJECT_ROOT / "data" / "seed"


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
        await session.execute(delete(SupplierRiskHistory))
        await session.execute(delete(Supplier))
        await session.execute(delete(RiskWeightConfig))
        await session.execute(delete(MitigationWeightConfig))
        await session.execute(delete(SystemConfig))

        await session.commit()

    print("Old seed data cleared.")


async def seed_suppliers() -> None:
    suppliers = load_json("suppliers.json")

    async with AsyncSessionLocal() as session:
        for supplier in suppliers:
            session.add(Supplier(**supplier))

        await session.commit()

    print(f"Suppliers inserted: {len(suppliers)}")


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
    await seed_risk_history()
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