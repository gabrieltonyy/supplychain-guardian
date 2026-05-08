import math
from statistics import mean, pstdev

from app.db.repositories.risk_history_repository import (
    RiskHistoryRepository,
)


class AnomalyDetectionService:
    """
    Database-backed anomaly detection service.

    Uses historical supplier risk scores
    to identify statistical spikes.
    """

    def __init__(
        self,
        risk_history_repository: RiskHistoryRepository,
        zscore_threshold: float = 2.5,
    ):
        self.repository = risk_history_repository
        self.zscore_threshold = zscore_threshold

    async def detect_supplier_anomaly(
        self,
        supplier_id: str,
        current_score: float,
    ) -> dict:
        historical_scores = (
            await self.repository.get_recent_scores(
                supplier_id=supplier_id,
                limit=12,
            )
        )

        if len(historical_scores) < 3:
            return {
                "is_anomaly": False,
                "reason": "insufficient_history",
                "baseline_mean": None,
                "z_score": None,
                "direction": None,
            }

        baseline_mean = mean(historical_scores)

        baseline_std = pstdev(historical_scores)

        if math.isclose(
            baseline_std,
            0.0,
        ):
            baseline_std = 1.0

        z_score = (
            current_score - baseline_mean
        ) / baseline_std

        is_anomaly = (
            abs(z_score)
            >= self.zscore_threshold
        )

        direction = (
            "spike"
            if z_score > 0
            else "drop"
        )

        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 2),
            "baseline_mean": round(
                baseline_mean,
                2,
            ),
            "baseline_std": round(
                baseline_std,
                2,
            ),
            "direction": direction,
            "history_points": len(
                historical_scores
            ),
            "historical_scores": historical_scores,
        }