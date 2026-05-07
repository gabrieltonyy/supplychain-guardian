from app.schemas.assessments import RiskAssessment, RiskLevel
from app.schemas.signals import SignalEvent, SignalType


DEFAULT_RISK_WEIGHTS: dict[SignalType, float] = {
    SignalType.FINANCIAL: 0.30,
    SignalType.GEOPOLITICAL: 0.25,
    SignalType.LOGISTICS: 0.20,
    SignalType.WEATHER: 0.15,
    SignalType.TARIFF: 0.10,
}


def compute_risk_score(
    signals: list[SignalEvent],
    weights: dict[SignalType, float] | None = None,
) -> RiskAssessment:
    """
    Compute supplier risk score from normalized signal events.

    Rules:
    - group by signal type,
    - use worst-case severity per signal type,
    - multiply severity by confidence,
    - apply weighted aggregation,
    - return score from 0 to 100.
    """

    if not signals:
        raise ValueError("At least one signal is required to compute risk score")

    active_weights = weights or DEFAULT_RISK_WEIGHTS

    supplier_id = signals[0].supplier_id

    by_type: dict[SignalType, float] = {}

    for signal in signals:
        adjusted_severity = signal.severity * signal.confidence
        current = by_type.get(signal.signal_type, 0.0)

        by_type[signal.signal_type] = max(
            current,
            adjusted_severity,
        )

    raw_score = sum(
        active_weights.get(signal_type, 0.0) * severity
        for signal_type, severity in by_type.items()
    )

    score = round(raw_score * 100, 1)

    level = classify_risk_level(score)

    return RiskAssessment(
        supplier_id=supplier_id,
        score=score,
        level=level,
        factor_breakdown={
            signal_type.value: round(severity * 100, 1)
            for signal_type, severity in by_type.items()
        },
        contributing_signals=sorted(
            {signal.source for signal in signals}
        ),
    )


def classify_risk_level(score: float) -> RiskLevel:
    """
    Classify numeric score into business risk level.
    """

    if score >= 75:
        return RiskLevel.CRITICAL

    if score >= 50:
        return RiskLevel.HIGH

    if score >= 25:
        return RiskLevel.MEDIUM

    return RiskLevel.LOW