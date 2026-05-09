from app.ingestion.financial_fetcher import financial_fetcher
from app.ingestion.geopolitical_fetcher import geopolitical_fetcher
from app.ingestion.logistics_fetcher import logistics_fetcher
from app.ingestion.weather_fetcher import weather_fetcher
from app.schemas.signals import SignalEvent


class LiveSignalIngestionService:
    async def ingest_supplier_signals(
        self,
        supplier_id: str,
        country: str,
        region: str,
        stock_symbol: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[SignalEvent]:

        signals: list[SignalEvent] = []

        # Financial
        if stock_symbol:
            try:
                financial_signal = await financial_fetcher.fetch(
                    supplier_id=supplier_id,
                    region=region,
                    symbol=stock_symbol,
                )
                signals.append(financial_signal)

            except Exception as exc:
                print(f"[financial_fetcher] {type(exc).__name__}: {exc}")

        # Geopolitical
        try:
            geopolitical_signal = await geopolitical_fetcher.fetch(
                supplier_id=supplier_id,
                region=region,
                query=f"{country} supply chain",
            )
            signals.append(geopolitical_signal)

        except Exception as exc:
            print(f"[geopolitical_fetcher] {type(exc).__name__}: {exc}")

        # Weather
        if latitude is not None and longitude is not None:
            try:
                weather_signal = await weather_fetcher.fetch(
                    supplier_id=supplier_id,
                    region=region,
                    lat=latitude,
                    lon=longitude,
                )
                signals.append(weather_signal)

            except Exception as exc:
                print(f"[weather_fetcher] {type(exc).__name__}: {exc}")

        # Logistics
        try:
            logistics_signal = await logistics_fetcher.fetch(
                supplier_id=supplier_id,
                region=region,
            )
            signals.append(logistics_signal)

        except Exception as exc:
            print(f"[logistics_fetcher] {type(exc).__name__}: {exc}")

        return signals


live_signal_ingestion_service = LiveSignalIngestionService()