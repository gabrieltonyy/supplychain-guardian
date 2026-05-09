import os
from typing import Any

import httpx


class OllamaClient:
    """
    Local fallback LLM client.

    Uses already-installed quantized Ollama models.
    Only called when explicitly requested.
    """

    def __init__(self) -> None:
        self.enabled = (
            os.getenv("OLLAMA_ENABLED", "true").lower()
            == "true"
        )
        self.base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ).rstrip("/")
        self.primary_model = os.getenv(
            "OLLAMA_PRIMARY_MODEL",
            "qwen2.5:7b",
        )
        self.fallback_model = os.getenv(
            "OLLAMA_FALLBACK_MODEL",
            "llama3.1:8b",
        )
        self.timeout_seconds = float(
            os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "45")
        )
        self.temperature = float(
            os.getenv("LLM_TEMPERATURE", "0.2")
        )

    def is_available(self) -> bool:
        return self.enabled

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
    ) -> str:
        if not self.is_available():
            raise RuntimeError("Ollama fallback is disabled")

        selected_model = model or self.primary_model

        payload: dict[str, Any] = {
            "model": selected_model,
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
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_ctx": 4096,
            },
        }

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

        return (
            data.get("message", {})
            .get("content", "")
            .strip()
        )

    async def generate_with_fallback(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        try:
            return await self.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.primary_model,
            )

        except Exception:
            return await self.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model=self.fallback_model,
            )


ollama_client = OllamaClient()