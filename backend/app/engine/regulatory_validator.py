import asyncio

from app.schemas.compliance import (
    RegulatoryCheck,
    RegulatoryResult,
)


NON_ADEQUACY_COUNTRIES = {
    "IN",
    "VN",
    "BD",
    "PK",
    "CN",
    "MX",
    "BR",
}


CONTROLLED_CATEGORIES = {
    "dual_use_electronics",
    "cryptography",
    "aerospace_components",
}


TRADE_RESTRICTED_COUNTRIES = {
    "IR",
    "KP",
    "SY",
    "CU",
    "RU",
}


def check_gdpr(
    supplier: dict,
    order: dict,
) -> RegulatoryResult:
    """
    GDPR cross-border transfer validation.
    """

    _ = order

    country = supplier.get("country_code") or supplier.get("country")

    needs_transfer_mechanism = (
        country in NON_ADEQUACY_COUNTRIES
    )

    has_dpa = (
        supplier.get("data_processing_agreement")
        is not None
    )

    if needs_transfer_mechanism and not has_dpa:
        return RegulatoryResult(
            check_type=RegulatoryCheck.GDPR_DATA_TRANSFER,
            passed=False,
            details=(
                f"Supplier in {country} — "
                f"no DPA on file"
            ),
            applicable_regulation=(
                "GDPR Art. 46"
            ),
            remediation=(
                "Obtain Standard Contractual Clauses "
                "(SCCs) before sharing PII"
            ),
        )

    return RegulatoryResult(
        check_type=RegulatoryCheck.GDPR_DATA_TRANSFER,
        passed=True,
        details=(
            "DPA in place or adequacy decision exists"
        ),
        applicable_regulation="GDPR Art. 45/46",
    )


def check_export_control(
    supplier: dict,
    order: dict,
) -> RegulatoryResult:
    """
    Export control validation.
    """

    country = supplier.get("country_code") or supplier.get("country")

    controlled_items = [
        item
        for item in order["line_items"]
        if item.get("category")
        in CONTROLLED_CATEGORIES
    ]

    restricted_destinations = {
        "CN",
        "RU",
        "IR",
    }

    if controlled_items and country in restricted_destinations:
        return RegulatoryResult(
            check_type=RegulatoryCheck.EXPORT_CONTROL,
            passed=False,
            details=(
                f"Controlled goods detected for "
                f"restricted destination {country}"
            ),
            applicable_regulation="EAR Part 774 / ITAR",
            remediation=(
                "Export licence required before procurement"
            ),
        )

    return RegulatoryResult(
        check_type=RegulatoryCheck.EXPORT_CONTROL,
        passed=True,
        details="No export-control restrictions triggered",
        applicable_regulation="EAR Part 774",
    )


def check_trade_restriction(
    supplier: dict,
    order: dict,
) -> RegulatoryResult:
    """
    Trade restriction validation.
    """

    _ = order

    country = supplier.get("country_code") or supplier.get("country")

    restricted = (
        country in TRADE_RESTRICTED_COUNTRIES
    )

    return RegulatoryResult(
        check_type=RegulatoryCheck.TRADE_RESTRICTION,
        passed=not restricted,
        details=(
            f"Country {country} "
            f"{'is' if restricted else 'is not'} "
            f"trade restricted"
        ),
        applicable_regulation=(
            "OFAC / EU Regulation 833/2014"
        ),
        remediation=(
            "Engage legal counsel before procurement"
            if restricted
            else None
        ),
    )


def check_tariff_classification(
    supplier: dict,
    order: dict,
) -> RegulatoryResult:
    """
    Verify all SKUs contain HS codes.
    """

    _ = supplier

    missing = [
        item["sku"]
        for item in order["line_items"]
        if not item.get("hs_code")
    ]

    return RegulatoryResult(
        check_type=RegulatoryCheck.TARIFF_CLASSIFICATION,
        passed=len(missing) == 0,
        details=(
            f"Missing HS codes on: {missing}"
            if missing
            else "All line items contain HS codes"
        ),
        applicable_regulation=(
            "WCO Harmonized System"
        ),
        remediation=(
            "Classify missing SKUs before customs submission"
            if missing
            else None
        ),
    )


def check_dual_use(
    supplier: dict,
    order: dict,
) -> RegulatoryResult:
    """
    Dual-use goods validation.
    """

    country = supplier.get("country_code") or supplier.get("country")

    dual_use_items = [
        item
        for item in order["line_items"]
        if item.get("category")
        == "dual_use_electronics"
    ]

    approved_countries = {
        "US",
        "GB",
        "DE",
        "FR",
        "JP",
        "AU",
    }

    requires_licence = (
        bool(dual_use_items)
        and country not in approved_countries
    )

    return RegulatoryResult(
        check_type=RegulatoryCheck.DUAL_USE_GOODS,
        passed=not requires_licence,
        details=(
            f"Dual-use items: "
            f"{[i['sku'] for i in dual_use_items]}"
            if dual_use_items
            else "No dual-use goods detected"
        ),
        applicable_regulation=(
            "EU Dual-Use Regulation 2021/821"
        ),
        remediation=(
            "Dual-use export licence required"
            if requires_licence
            else None
        ),
    )


async def run_regulatory_checks(
    supplier: dict,
    order: dict,
) -> list[RegulatoryResult]:
    """
    Run all compliance checks concurrently.
    """

    return await asyncio.gather(
        asyncio.to_thread(
            check_gdpr,
            supplier,
            order,
        ),
        asyncio.to_thread(
            check_export_control,
            supplier,
            order,
        ),
        asyncio.to_thread(
            check_trade_restriction,
            supplier,
            order,
        ),
        asyncio.to_thread(
            check_tariff_classification,
            supplier,
            order,
        ),
        asyncio.to_thread(
            check_dual_use,
            supplier,
            order,
        ),
    )