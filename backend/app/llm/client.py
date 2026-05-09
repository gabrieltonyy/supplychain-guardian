import os
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class LLMClient:
    """
    AMD-first, request-triggered LLM client.

    Priority:
    1. AMD Cloud vLLM endpoint
    2. Local Ollama primary model
    3. Local Ollama fallback model
    4. Deterministic fallback summary
    """

    def __init__(self) -> None:
        self.last_provider_used: str | None = None

        self.enable_reasoning = (
            os.getenv("ENABLE_LLM_REASONING", "false").lower()
            == "true"
        )

        self.provider = os.getenv(
            "LLM_PROVIDER",
            getattr(settings, "LLM_PROVIDER", "amd"),
        ).lower()

        self.enable_fallback = (
            os.getenv("LLM_ENABLE_FALLBACK", "true").lower()
            == "true"
        )

        self.amd_enabled = (
            os.getenv("AMD_LLM_ENABLED", "false").lower()
            == "true"
        )
        self.amd_inference_url = os.getenv(
            "AMD_INFERENCE_URL",
            "",
        )
        self.amd_model_name = os.getenv(
            "AMD_MODEL_NAME",
            "Qwen/Qwen2.5-7B-Instruct",
        )

        self.ollama_enabled = (
            os.getenv("OLLAMA_ENABLED", "true").lower()
            == "true"
        )
        self.ollama_base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ).rstrip("/")
        self.ollama_primary_model = os.getenv(
            "OLLAMA_PRIMARY_MODEL",
            "qwen2.5:7b",
        )
        self.ollama_fallback_model = os.getenv(
            "OLLAMA_FALLBACK_MODEL",
            "llama3.1:8b",
        )

        self.timeout_seconds = float(
            os.getenv("LLM_REQUEST_TIMEOUT_SECONDS", "45")
        )
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "400"))
        self.temperature = float(
            os.getenv("LLM_TEMPERATURE", "0.2")
        )

    async def ainvoke(
        self,
        prompt: str,
        force: bool = False,
    ) -> str:
        self.last_provider_used = None

        if not force and not self.enable_reasoning:
            self.last_provider_used = "deterministic_fallback"
            return self._fallback_summary(prompt)

        if self.provider == "amd":
            try:
                result = await self._invoke_amd(prompt)
                self.last_provider_used = "amd_vllm"
                return result

            except Exception as exc:
                logger.warning(
                    "AMD LLM failed, fallback=%s, error=%s",
                    self.enable_fallback,
                    exc,
                )

                if not self.enable_fallback:
                    self.last_provider_used = "deterministic_fallback"
                    return self._fallback_summary(prompt)

        if self.enable_fallback:
            try:
                result = await self._invoke_ollama_with_fallback(prompt)
                self.last_provider_used = "ollama"
                return result

            except Exception as exc:
                logger.warning(
                    "Ollama fallback failed, using deterministic "
                    "fallback. error=%s",
                    exc,
                )

        self.last_provider_used = "deterministic_fallback"
        return self._fallback_summary(prompt)

    async def achat(
        self,
        system_prompt: str,
        user_prompt: str,
        force: bool = False,
    ) -> str:
        prompt = (
            f"System:\n{system_prompt}\n\n"
            f"User:\n{user_prompt}"
        )

        return await self.ainvoke(
            prompt=prompt,
            force=force,
        )

    async def _invoke_amd(
        self,
        prompt: str,
    ) -> str:
        if not self.amd_enabled:
            raise RuntimeError("AMD LLM is disabled")

        if not self.amd_inference_url:
            raise RuntimeError("AMD_INFERENCE_URL is missing")

        payload: dict[str, Any] = {
            "model": self.amd_model_name,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a concise enterprise supply chain "
                        "risk reasoning assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            response = await client.post(
                self.amd_inference_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()
            data = response.json()

        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )

        if not content:
            raise RuntimeError("AMD LLM returned empty content")

        return content

    async def _invoke_ollama_with_fallback(
        self,
        prompt: str,
    ) -> str:
        if not self.ollama_enabled:
            raise RuntimeError("Ollama is disabled")

        try:
            return await self._invoke_ollama(
                prompt=prompt,
                model=self.ollama_primary_model,
            )

        except Exception as primary_exc:
            logger.warning(
                "Primary Ollama model failed: %s",
                primary_exc,
            )

            return await self._invoke_ollama(
                prompt=prompt,
                model=self.ollama_fallback_model,
            )

    async def _invoke_ollama(
        self,
        prompt: str,
        model: str,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a concise enterprise supply chain "
                        "risk reasoning assistant."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
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
                f"{self.ollama_base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

        content = (
            data.get("message", {})
            .get("content", "")
            .strip()
        )

        if not content:
            raise RuntimeError(
                f"Ollama model {model} returned empty content"
            )

        return content

    def _fallback_summary(
        self,
        prompt: str,
    ) -> str:
        prompt_lower = prompt.lower()

        if "critical" in prompt_lower:
            return (
                "The supplier shows critical risk based on the current "
                "signal breakdown. Immediate review is recommended "
                "because the data indicates elevated disruption exposure."
            )

        if "high" in prompt_lower:
            return (
                "The supplier shows high risk based on the current "
                "signal breakdown. Mitigation planning should begin "
                "because several risk factors are elevated."
            )

        if "medium" in prompt_lower:
            return (
                "The supplier shows moderate risk based on the current "
                "signal breakdown. Continued monitoring is recommended "
                "before execution."
            )

        return (
            "The supplier currently shows low risk based on the "
            "available signals. No immediate mitigation action is "
            "required."
        )


llm = LLMClient()