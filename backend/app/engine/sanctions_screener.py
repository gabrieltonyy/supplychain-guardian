from datetime import datetime, UTC

from app.schemas.compliance import (
    SanctionsHitSeverity,
    SanctionsResult,
)


SANCTIONS_LISTS = {
    "OFAC_SDN": "ofac_sdn_list",
    "UN_SECURITY": "un_security_council_list",
    "EU_CONSOLIDATED": "eu_consolidated_list",
    "INTERNAL_BLOCK": "internal_blocklist",
}


HIGH_RISK_COUNTRIES = {
    "IR",
    "KP",
    "SY",
    "CU",
    "VE",
}


MEDIUM_RISK_COUNTRIES = {
    "RU",
    "BY",
    "MM",
    "SD",
    "LY",
}


MOCK_SANCTIONS_ENTRIES = {
    "OFAC_SDN": [
        "Blocked Supplier Trading",
        "Red Star Industrial Group",
    ],
    "UN_SECURITY": [
        "Global Restricted Logistics",
    ],
    "EU_CONSOLIDATED": [
        "Advisory Components Export",
    ],
    "INTERNAL_BLOCK": [
        "Internal Blocked Vendor",
    ],
}


def simple_similarity(
    left: str,
    right: str,
) -> float:
    """
    Lightweight fuzzy similarity fallback.

    This avoids adding rapidfuzz immediately.
    Returns value from 0.0 to 1.0.
    """

    left_tokens = set(left.lower().replace(",", "").split())
    right_tokens = set(right.lower().replace(",", "").split())

    if not left_tokens or not right_tokens:
        return 0.0

    overlap = left_tokens.intersection(right_tokens)
    union = left_tokens.union(right_tokens)

    return len(overlap) / len(union)


async def screen_supplier(
    supplier: dict,
    fuzzy_threshold: float = 0.85,
) -> SanctionsResult:
    """
    Screen one supplier against country risk and mock sanctions lists.
    """

    supplier_id = supplier["id"]
    name = supplier["name"]
    country = supplier.get("country_code") or supplier.get("country")

    hits: list[tuple[str, float]] = []

    if country in HIGH_RISK_COUNTRIES:
        return SanctionsResult(
            supplier_id=supplier_id,
            supplier_name=name,
            supplier_country=country,
            hit_severity=SanctionsHitSeverity.BLOCKED,
            matched_lists=["COUNTRY_HIGH_RISK"],
            match_confidence=1.0,
            screened_at=datetime.now(UTC),
        )

    if country in MEDIUM_RISK_COUNTRIES:
        hits.append(("COUNTRY_MEDIUM_RISK", 1.0))

    for list_name, entries in MOCK_SANCTIONS_ENTRIES.items():
        for entry_name in entries:
            score = simple_similarity(name, entry_name)

            if score >= fuzzy_threshold:
                hits.append((list_name, score))

    if not hits:
        severity = SanctionsHitSeverity.CLEAR
    elif any(
        hit[0] in {"OFAC_SDN", "UN_SECURITY", "INTERNAL_BLOCK"}
        for hit in hits
    ):
        severity = SanctionsHitSeverity.BLOCKED
    else:
        severity = SanctionsHitSeverity.ADVISORY

    return SanctionsResult(
        supplier_id=supplier_id,
        supplier_name=name,
        supplier_country=country,
        hit_severity=severity,
        matched_lists=[hit[0] for hit in hits],
        match_confidence=max((hit[1] for hit in hits), default=0.0),
        screened_at=datetime.now(UTC),
    )


async def screen_all_suppliers(
    suppliers: list[dict],
) -> list[SanctionsResult]:
    """
    Screen all suppliers.
    """

    results = []

    for supplier in suppliers:
        results.append(
            await screen_supplier(supplier)
        )

    return results