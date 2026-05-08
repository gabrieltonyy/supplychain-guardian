from datetime import datetime, timedelta, UTC
from uuid import NAMESPACE_DNS, uuid5

from app.schemas.execution import RFQDocument, RFQLineItem


def generate_rfq(
    option: dict,
    supplier: dict,
    original_order: dict,
    plan_id: str,
) -> RFQDocument:
    """
    Generate a deterministic RFQ document.

    The RFQ ID is deterministic from plan_id + supplier_id,
    so retries do not create duplicate RFQs.
    """

    rfq_id = str(
        uuid5(
            NAMESPACE_DNS,
            f"{plan_id}:{option['supplier_id']}",
        )
    )

    risk_level = original_order.get("risk_level", "HIGH")

    if risk_level == "CRITICAL":
        deadline = datetime.now(UTC) + timedelta(hours=48)
    else:
        deadline = datetime.now(UTC) + timedelta(days=5)

    line_items: list[RFQLineItem] = []

    for item in original_order["line_items"]:
        supplier_capacity = supplier.get(
            "capacity_units_per_month",
            item["quantity"],
        )

        fulfillable_qty = min(
            item["quantity"],
            supplier_capacity,
        )

        target_price = item["unit_cost"] * (
            1 + option["cost_delta_pct"] / 100
        )

        line_items.append(
            RFQLineItem(
                sku=item["sku"],
                description=item["description"],
                quantity=fulfillable_qty,
                unit=item["unit"],
                target_price=round(target_price, 2),
                notes=(
                    f"Replacing order from "
                    f"{original_order['supplier_name']} — expedited requirement"
                ),
            )
        )

    return RFQDocument(
        rfq_id=rfq_id,
        supplier_id=option["supplier_id"],
        supplier_name=supplier["name"],
        supplier_email=supplier["contact_email"],
        line_items=line_items,
        response_deadline=deadline,
        delivery_destination=original_order["destination"],
        terms_ref="SCG-TERMS-V2",
        generated_at=datetime.now(UTC),
    )