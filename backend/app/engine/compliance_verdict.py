from app.schemas.compliance import (
    ComplianceVerdict,
    RegulatoryCheck,
    RegulatoryResult,
    SanctionsHitSeverity,
    SanctionsResult,
)


HARD_FAIL_REGULATORY_CHECKS = {
    RegulatoryCheck.EXPORT_CONTROL,
    RegulatoryCheck.TRADE_RESTRICTION,
    RegulatoryCheck.DUAL_USE_GOODS,
}


def compute_compliance_verdict(
    sanctions_results: list[SanctionsResult],
    regulatory_results: list[RegulatoryResult],
) -> tuple[ComplianceVerdict, str]:
    """
    Deterministically compute compliance verdict.

    Rules:
    - blocked sanctions hit => BLOCKED
    - hard regulatory failure => BLOCKED
    - advisory sanctions hit => FLAGGED
    - soft regulatory failure => FLAGGED
    - otherwise => CLEARED
    """

    has_blocked_sanctions = any(
        result.hit_severity == SanctionsHitSeverity.BLOCKED
        for result in sanctions_results
    )

    has_advisory_sanctions = any(
        result.hit_severity == SanctionsHitSeverity.ADVISORY
        for result in sanctions_results
    )

    has_hard_regulatory_failure = any(
        not result.passed
        and result.check_type in HARD_FAIL_REGULATORY_CHECKS
        for result in regulatory_results
    )

    has_soft_regulatory_failure = any(
        not result.passed
        for result in regulatory_results
    )

    if has_blocked_sanctions:
        return (
            ComplianceVerdict.BLOCKED,
            "One or more suppliers matched a blocked sanctions condition.",
        )

    if has_hard_regulatory_failure:
        return (
            ComplianceVerdict.BLOCKED,
            "One or more hard regulatory checks failed.",
        )

    if has_advisory_sanctions:
        return (
            ComplianceVerdict.FLAGGED,
            "One or more suppliers triggered advisory sanctions review.",
        )

    if has_soft_regulatory_failure:
        return (
            ComplianceVerdict.FLAGGED,
            "One or more non-blocking regulatory checks require review.",
        )

    return (
        ComplianceVerdict.CLEARED,
        "All sanctions screenings are clear and all regulatory checks passed.",
    )