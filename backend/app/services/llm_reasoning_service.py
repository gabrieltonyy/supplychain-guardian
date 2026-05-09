import json
from pathlib import Path
from typing import Any

from app.llm.client import llm_client


PROMPT_DIR = Path(__file__).resolve().parent.parent / "llm" / "prompts"


class LlmReasoningService:
    def _load_prompt(
        self,
        filename: str,
    ) -> str:
        path = PROMPT_DIR / filename

        if not path.exists():
            return "You are a concise supply chain AI assistant."

        return path.read_text(encoding="utf-8").strip()

    async def generate_risk_reasoning(
        self,
        risk_assessment: Any,
        anomaly_detection: Any | None = None,
        signals: list[Any] | None = None,
        force: bool = False,
    ) -> str | None:
        system_prompt = self._load_prompt("risk_reasoning.txt")

        payload = {
            "risk_assessment": self._safe_dump(risk_assessment),
            "anomaly_detection": self._safe_dump(anomaly_detection),
            "signals": [
                self._safe_dump(signal)
                for signal in (signals or [])
            ],
        }

        return await llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=json.dumps(
                payload,
                indent=2,
                default=str,
            ),
            force=force,
        )

    async def generate_mitigation_justification(
        self,
        mitigation_plan: Any,
        force: bool = False,
    ) -> str | None:
        system_prompt = self._load_prompt(
            "mitigation_justification.txt"
        )

        return await llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=json.dumps(
                self._safe_dump(mitigation_plan),
                indent=2,
                default=str,
            ),
            force=force,
        )

    async def generate_compliance_summary(
        self,
        compliance_result: Any,
        force: bool = False,
    ) -> str | None:
        system_prompt = self._load_prompt(
            "compliance_summary.txt"
        )

        return await llm_client.generate(
            system_prompt=system_prompt,
            user_prompt=json.dumps(
                self._safe_dump(compliance_result),
                indent=2,
                default=str,
            ),
            force=force,
        )

    def _safe_dump(
        self,
        value: Any,
    ) -> Any:
        if value is None:
            return None

        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        if isinstance(value, dict):
            return value

        return str(value)


llm_reasoning_service = LlmReasoningService()