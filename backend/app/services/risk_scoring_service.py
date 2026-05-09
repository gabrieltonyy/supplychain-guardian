import os

from app.schemas.signals import SignalEvent


class RiskScoringService:
    SIGNAL_WEIGHTS = {
        "financial": 0.35,
        "geopolitical": 0.30,
        "weather": 0.15,
        "logistics": 0.20,
    }

    async def calculate_risk_score(
        self,
        supplier_id: str,
        signals: list[SignalEvent],
    ) -> dict:
        weighted_total = 0.0
        factor_breakdown = {}

        for signal in signals:
            signal_type = (
                signal.signal_type.value
                if hasattr(signal.signal_type, "value")
                else str(signal.signal_type)
            )

            weight = self.SIGNAL_WEIGHTS.get(signal_type, 0.0)

            severity = signal.severity

            if self._demo_stress_enabled(supplier_id):
                severity = self._apply_demo_stress(
                    signal_type=signal_type,
                    severity=severity,
                )

            weighted_score = severity * weight

            factor_breakdown[signal_type] = round(
                weighted_score * 100,
                2,
            )

            weighted_total += weighted_score

        final_score = round(weighted_total * 100, 2)

        if final_score >= 70:
            level = "CRITICAL"
        elif final_score >= 50:
            level = "HIGH"
        elif final_score >= 25:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "supplier_id": supplier_id,
            "score": final_score,
            "level": level,
            "factor_breakdown": factor_breakdown,
            "signal_count": len(signals),
            "demo_stress_mode": self._demo_stress_enabled(
                supplier_id
            ),
            "contributing_signals": [
                (
                    signal.source.value
                    if hasattr(signal.source, "value")
                    else str(signal.source)
                )
                for signal in signals
            ],
        }

    def _demo_stress_enabled(
        self,
        supplier_id: str,
    ) -> bool:
        enabled = os.getenv(
            "DEMO_STRESS_MODE",
            "false",
        ).lower() == "true"

        if not enabled:
            return False

        suppliers = {
            item.strip()
            for item in os.getenv(
                "DEMO_STRESS_SUPPLIERS",
                "",
            ).split(",")
            if item.strip()
        }

        return supplier_id in suppliers

    def _apply_demo_stress(
        self,
        signal_type: str,
        severity: float,
    ) -> float:
        stress_floor = {
            "financial": 0.80,
            "geopolitical": 0.85,
            "weather": 0.45,
            "logistics": 0.70,
        }

        return max(
            severity,
            stress_floor.get(signal_type, severity),
        )


risk_scoring_service = RiskScoringService()