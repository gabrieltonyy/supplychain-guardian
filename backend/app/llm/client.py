from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)


class LLMClient:
    """
    Lightweight LLM wrapper.

    For MVP:
    - returns deterministic fallback summaries when no LLM is available.
    - later can call Ollama, OpenAI, or AMD-hosted inference endpoint.
    """

    async def ainvoke(self, prompt: str) -> str:
        """
        Async LLM invocation entrypoint.
        """

        provider = settings.LLM_PROVIDER.lower()

        if provider == "ollama":
            return await self._invoke_ollama_or_fallback(prompt)

        if provider == "openai":
            return await self._invoke_openai_or_fallback(prompt)

        return self._fallback_summary(prompt)

    async def _invoke_ollama_or_fallback(self, prompt: str) -> str:
        """
        Placeholder for Ollama integration.
        """

        logger.info("Using fallback LLM response for provider=ollama")
        return self._fallback_summary(prompt)

    async def _invoke_openai_or_fallback(self, prompt: str) -> str:
        """
        Placeholder for OpenAI integration.
        """

        logger.info("Using fallback LLM response for provider=openai")
        return self._fallback_summary(prompt)

    def _fallback_summary(self, prompt: str) -> str:
        """
        Deterministic fallback reasoning.

        This keeps the workflow functional before external LLM wiring.
        """

        prompt_lower = prompt.lower()

        if "critical" in prompt_lower:
            return (
                "The supplier shows critical risk based on the current signal "
                "breakdown. Immediate review is recommended because the data "
                "indicates elevated disruption exposure."
            )

        if "high" in prompt_lower:
            return (
                "The supplier shows high risk based on the current signal "
                "breakdown. Mitigation planning should begin because several "
                "risk factors are elevated."
            )

        if "medium" in prompt_lower:
            return (
                "The supplier shows moderate risk based on the current signal "
                "breakdown. Continued monitoring is recommended before execution."
            )

        return (
            "The supplier currently shows low risk based on the available "
            "signals. No immediate mitigation action is required."
        )


llm = LLMClient()