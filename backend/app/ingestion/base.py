from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.exceptions import ExternalServiceException
from app.core.logging import get_logger
from app.schemas.signals import SignalEvent


logger = get_logger(__name__)


class BaseSignalFetcher(ABC):
    """
    Base class for all external signal fetchers.

    Every fetcher must:
    - call one external or mock data source,
    - normalize the result,
    - return one or more SignalEvent objects.
    """

    source_name: str
    timeout_seconds: float = 15.0

    async def get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an async HTTP GET request and return JSON.
        """

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=headers,
                )

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as exc:
            logger.error(
                "%s returned HTTP %s",
                self.source_name,
                exc.response.status_code,
            )
            raise ExternalServiceException(
                message=f"{self.source_name} returned an HTTP error",
                error_code="EXTERNAL_HTTP_ERROR",
            ) from exc

        except httpx.TimeoutException as exc:
            logger.error("%s request timed out", self.source_name)
            raise ExternalServiceException(
                message=f"{self.source_name} request timed out",
                error_code="EXTERNAL_TIMEOUT",
            ) from exc

        except httpx.RequestError as exc:
            logger.error("%s request failed: %s", self.source_name, str(exc))
            raise ExternalServiceException(
                message=f"{self.source_name} request failed",
                error_code="EXTERNAL_REQUEST_ERROR",
            ) from exc

        except ValueError as exc:
            logger.error("%s returned invalid JSON", self.source_name)
            raise ExternalServiceException(
                message=f"{self.source_name} returned invalid JSON",
                error_code="EXTERNAL_INVALID_JSON",
            ) from exc

    @abstractmethod
    async def fetch(self, *args: Any, **kwargs: Any) -> SignalEvent | list[SignalEvent]:
        """
        Fetch and normalize external data into SignalEvent object(s).
        """
        raise NotImplementedError