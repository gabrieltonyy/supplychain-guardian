from app.integrations.signal_types import (
    ExternalSignalSource,
    ExternalSignalType,
    NormalizedExternalSignal,
)


def normalize_gdelt_article(
    article: dict,
    supplier_id: str | None = None,
    country: str | None = None,
) -> NormalizedExternalSignal:
    title = article.get("title") or "GDELT geopolitical signal"
    source_country = article.get("sourcecountry") or country

    severity = _score_gdelt_title(title)

    return NormalizedExternalSignal(
        supplier_id=supplier_id,
        source=ExternalSignalSource.GDELT,
        signal_type=ExternalSignalType.GEOPOLITICAL,
        severity=severity,
        confidence=0.75,
        title=title,
        summary=article.get("url"),
        country=source_country,
        raw_payload=article,
    )


def normalize_openmeteo_current(
    payload: dict,
    supplier_id: str | None = None,
    country: str | None = None,
    region: str | None = None,
) -> NormalizedExternalSignal:
    current = payload.get("current", {})

    precipitation = float(current.get("precipitation") or 0)
    wind_speed = float(current.get("wind_speed_10m") or 0)
    temperature = float(current.get("temperature_2m") or 0)

    severity = 0.0

    if precipitation >= 20:
        severity += 45
    elif precipitation >= 10:
        severity += 30
    elif precipitation >= 2:
        severity += 15

    if wind_speed >= 60:
        severity += 45
    elif wind_speed >= 35:
        severity += 25
    elif wind_speed >= 20:
        severity += 10

    if temperature >= 40 or temperature <= -5:
        severity += 15

    severity = min(severity, 100.0)

    return NormalizedExternalSignal(
        supplier_id=supplier_id,
        source=ExternalSignalSource.OPEN_METEO,
        signal_type=ExternalSignalType.WEATHER,
        severity=severity,
        confidence=0.85,
        title="Current weather logistics signal",
        summary=(
            f"temperature={temperature}, "
            f"precipitation={precipitation}, "
            f"wind_speed={wind_speed}"
        ),
        country=country,
        region=region,
        raw_payload=payload,
    )


def normalize_finnhub_quote(
    payload: dict,
    supplier_id: str | None = None,
    symbol: str | None = None,
) -> NormalizedExternalSignal:
    current_price = float(payload.get("c") or 0)
    previous_close = float(payload.get("pc") or 0)

    pct_change = 0.0

    if previous_close > 0:
        pct_change = ((current_price - previous_close) / previous_close) * 100

    severity = min(abs(pct_change) * 8, 100.0)

    return NormalizedExternalSignal(
        supplier_id=supplier_id,
        source=ExternalSignalSource.FINNHUB,
        signal_type=ExternalSignalType.FINANCIAL,
        severity=round(severity, 2),
        confidence=0.8,
        title=f"Finnhub quote signal for {symbol or 'symbol'}",
        summary=f"price_change_pct={round(pct_change, 2)}",
        raw_payload=payload,
    )


def normalize_shipbob_response(
    payload: dict,
    supplier_id: str | None = None,
) -> NormalizedExternalSignal:
    severity = 0.0

    if isinstance(payload, dict):
        if payload.get("error"):
            severity = 50.0

    return NormalizedExternalSignal(
        supplier_id=supplier_id,
        source=ExternalSignalSource.SHIPBOB,
        signal_type=ExternalSignalType.LOGISTICS,
        severity=severity,
        confidence=0.65,
        title="ShipBob logistics signal",
        summary="Logistics response normalized",
        raw_payload=payload if isinstance(payload, dict) else {"data": payload},
    )


def _score_gdelt_title(
    title: str,
) -> float:
    lowered = title.lower()

    keywords = {
        "war": 80,
        "conflict": 75,
        "sanction": 75,
        "export control": 70,
        "restriction": 65,
        "strike": 65,
        "shutdown": 60,
        "supply chain": 45,
        "tariff": 55,
        "protest": 55,
        "port": 45,
        "delay": 40,
    }

    score = 20.0

    for keyword, keyword_score in keywords.items():
        if keyword in lowered:
            score = max(score, float(keyword_score))

    return min(score, 100.0)