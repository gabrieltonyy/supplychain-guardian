import statistics

from app.schemas.assessments import AnomalyDetection


def detect_anomaly(
    current_score: float,
    history: list[float],
    threshold: float = 2.0,
) -> AnomalyDetection:
    """
    Detect whether the current risk score is statistically unusual
    compared to historical supplier scores.

    Uses z-score against a rolling baseline.
    """

    if len(history) < 7:
        return AnomalyDetection(
            is_anomaly=False,
            reason="insufficient_history",
        )

    mean = statistics.mean(history)

    stdev = statistics.stdev(history)

    if stdev == 0:
        stdev = 1.0

    z_score = (current_score - mean) / stdev

    is_anomaly = abs(z_score) > threshold

    direction = "spike" if z_score > 0 else "drop"

    return AnomalyDetection(
        is_anomaly=is_anomaly,
        z_score=round(z_score, 2),
        baseline_mean=round(mean, 1),
        direction=direction,
        reason=None if is_anomaly else "within_baseline",
    )