"""Finance free sources — FRED, Alpha Vantage, CoinGecko, EDGAR, Companies House, World Bank, IMF."""

from __future__ import annotations

from rudra.core.config import Settings
from rudra.integrations.providers import FinanceLine
from rudra.jarvis.connectors.free_sources._http import get_json
from rudra.research.connectors import edgar_search


async def fetch_fred_lines(settings: Settings) -> list[FinanceLine]:
    key = settings.fred_api_key
    if not key:
        return []
    series = {"DFF": "Fed funds rate", "CPIAUCSL": "US CPI", "UNRATE": "US unemployment"}
    out: list[FinanceLine] = []
    for sid, label in series.items():
        data = await get_json(
            "https://api.stlouisfed.org/fred/series/observations",
            params={
                "series_id": sid,
                "api_key": key.get_secret_value(),
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            },
        )
        if not isinstance(data, dict):
            continue
        obs = data.get("observations", [])
        if obs and obs[0].get("value") not in (".", None):
            out.append(FinanceLine(label, float(obs[0]["value"]), "USD", sid))
    return out


async def fetch_alpha_vantage_lines(settings: Settings) -> list[FinanceLine]:
    key = settings.alpha_vantage_api_key
    symbols = [s.strip() for s in settings.ea_finance_watchlist.split(",") if s.strip()]
    if not key or not symbols:
        return []
    out: list[FinanceLine] = []
    for sym in symbols[:3]:
        data = await get_json(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": sym, "apikey": key.get_secret_value()},
        )
        if not isinstance(data, dict):
            continue
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        if price:
            out.append(FinanceLine(f"{sym} spot", float(price), "USD", "equity"))
    return out


async def fetch_coingecko_lines() -> list[FinanceLine]:
    data = await get_json(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "bitcoin,ethereum", "vs_currencies": "usd"},
    )
    if not isinstance(data, dict):
        return []
    out: list[FinanceLine] = []
    for coin, prices in data.items():
        usd = prices.get("usd")
        if usd is not None:
            out.append(FinanceLine(coin.title(), float(usd), "USD", "crypto"))
    return out


async def fetch_edgar_finance_lines(settings: Settings) -> list[FinanceLine]:
    sources = await edgar_search(settings.ea_edgar_watch_query, max_results=3)
    return [
        FinanceLine(s.title[:80], 0.0, "USD", "sec_filing")
        for s in sources
    ]


async def fetch_companies_house_lines(settings: Settings) -> list[FinanceLine]:
    key = settings.companies_house_api_key
    if not key:
        return []
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://api.company-information.service.gov.uk/search/companies",
                params={"q": "technology"},
                auth=(key, ""),
            )
            if r.status_code != 200:
                return []
            items = r.json().get("items", [])[:3]
            return [
                FinanceLine(i.get("title", "Company")[:80], 0.0, "GBP", "companies_house")
                for i in items
            ]
    except Exception:
        return []


async def fetch_worldbank_lines() -> list[FinanceLine]:
    data = await get_json(
        "https://api.worldbank.org/v2/country/USA/indicator/NY.GDP.MKTP.CD",
        params={"format": "json", "per_page": 1, "date": "2023:2024"},
    )
    if not isinstance(data, list) or len(data) < 2:
        return []
    records = data[1]
    if not records:
        return []
    val = records[0].get("value")
    if val is None:
        return []
    return [FinanceLine("US GDP (World Bank)", float(val), "USD", "macro")]


async def fetch_imf_lines() -> list[FinanceLine]:
    data = await get_json(
        "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/USA",
    )
    if not isinstance(data, dict):
        return []
    values = data.get("values", {}).get("NGDP_RPCH", {}).get("USA", {})
    if not values:
        return []
    year = sorted(values.keys())[-1]
    val = values[year]
    if val is None:
        return []
    return [FinanceLine("US GDP growth (IMF)", float(val), "USD", "macro")]
