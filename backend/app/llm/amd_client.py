import os
from typing import Any

import httpx


class AmdLlmClient:
    """
    AMD vLLM/OpenAI-compatible inference client.

    This client is only called when explicitly requested.
    It does not start or manage GPU instances.
    """

    def __init__(self) -> None:
        self.enabled = (
            os.getenv("AMD_LLM_ENABLED", "false").lower()
            == "true"
        )
        self.inference_url = os.getenv("AMD_INFERENCE_URL", "")
        self.model_name = os.getenv(
            "AMD_MODEL_NAME",
            "gpt-oss-120b",
        )
        self.timeout_seconds = float(
            os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "45")
        )
        self.max_tokens = int(
            os.getenv("LLM_MAX_TOKENS", "400")
        )
        self.temperature = float(
            os.getenv("LLM_TEMPERATURE", "0.2")
        )

    def is_available(self) -> bool:
        return bool(self.enabled and self.inference_url)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        if not self.is_available():
            raise RuntimeError(
                "AMD LLM is not enabled or AMD_INFERENCE_URL is missing"
            )

        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            response = await client.post(
                self.inference_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()
            data = response.json()

        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )


amd_llm_client = AmdLlmClient()