import json
import os

import httpx

from app.integrations.signal_normalizer import normalize_shipbob_response
from app.integrations.signal_types import NormalizedExternalSignal


class ShipBobClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 15.0,
    ):
        self.api_key = api_key or os.getenv("SHIPBOB_API_KEY")
        self.base_url = (
            base_url
            or os.getenv("SHIPBOB_BASE_URL")
            or "https://api.shipbob.com/2026-01"
        ).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> dict:
        if not self.api_key:
            raise ValueError("SHIPBOB_API_KEY is not configured")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "SupplyChainGuardian/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def _get(
        self,
        path: str,
    ) -> dict | list:
        url = f"{self.base_url}/{path.lstrip('/')}"

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = await client.get(
                url,
                headers=self._headers(),
            )

            if response.status_code in {401, 403}:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": "ShipBob authentication or permission failed",
                    "url": str(response.url),
                    "body": response.text[:300],
                }

            if response.status_code == 404:
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": "ShipBob endpoint not found",
                    "url": str(response.url),
                    "body": response.text[:300],
                }

            response.raise_for_status()

            try:
                return response.json()

            except json.JSONDecodeError as exc:
                preview = response.text[:300]
                raise ValueError(
                    "ShipBob returned non-JSON response. "
                    f"status={response.status_code}, "
                    f"url={response.url}, "
                    f"preview={preview}"
                ) from exc

    async def get_channel(
        self,
    ) -> dict | list:
        """
        Lightweight auth test endpoint for ShipBob Developer API.
        Use this before inventory because it requires less account setup.
        """

        return await self._get("/channel")

    async def get_inventory(
        self,
    ) -> dict | list:
        """
        Inventory endpoint. May require inventory/product setup and scopes.
        """

        return await self._get("/inventory")

    async def get_logistics_signal(
        self,
        supplier_id: str | None = None,
    ) -> NormalizedExternalSignal:
        payload = await self.get_channel()

        normalized_payload = (
            payload
            if isinstance(payload, dict)
            else {
                "channel_count": len(payload),
                "channels": payload[:5],
            }
        )

        return normalize_shipbob_response(
            payload=normalized_payload,
            supplier_id=supplier_id,
        )


shipbob_client = ShipBobClient()