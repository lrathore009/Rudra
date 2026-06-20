"""Travel free sources — Amadeus sandbox, OpenSky, Nominatim, RestCountries, OpenFlights reference."""

from __future__ import annotations

from rudra.core.config import Settings
from rudra.integrations.providers import TravelConfirmation
from rudra.jarvis.connectors.free_sources._http import get_json


async def _amadeus_token(settings: Settings) -> str | None:
    key = settings.amadeus_api_key
    secret = settings.amadeus_api_secret
    if not (key and secret):
        return None
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                "https://test.api.amadeus.com/v1/security/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": key,
                    "client_secret": secret.get_secret_value(),
                },
            )
            if r.status_code != 200:
                return None
            return r.json().get("access_token")
    except Exception:
        return None


async def fetch_amadeus_travel(settings: Settings) -> list[TravelConfirmation]:
    token = await _amadeus_token(settings)
    if not token:
        return []
    try:
        import httpx

        async with httpx.AsyncClient(timeout=12.0) as client:
            r = await client.get(
                "https://test.api.amadeus.com/v1/shopping/flight-destinations",
                params={"origin": "DXB", "maxPrice": "2000"},
                headers={"Authorization": f"Bearer {token}"},
            )
            if r.status_code != 200:
                return []
            data = r.json().get("data", [])[:3]
            return [
                TravelConfirmation(
                    f"Deal: {d.get('destination', '?')} from DXB",
                    "flight_deal",
                    None,
                    d.get("destination"),
                    "amadeus",
                )
                for d in data
            ]
    except Exception:
        return []


async def fetch_opensky_travel() -> list[TravelConfirmation]:
    data = await get_json("https://opensky-network.org/api/states/all", timeout=15.0)
    if not isinstance(data, dict):
        return []
    states = data.get("states") or []
    # Sample active flights over UAE-ish bbox
    count = 0
    out: list[TravelConfirmation] = []
    for s in states:
        if len(s) < 8:
            continue
        lat, lon = s[6], s[7]
        if lat is None or lon is None:
            continue
        if 22 <= lat <= 27 and 51 <= lon <= 57:
            callsign = (s[1] or "").strip()
            if callsign:
                out.append(
                    TravelConfirmation(
                        f"Active flight {callsign}",
                        "opensky",
                        None,
                        f"{lat:.1f},{lon:.1f}",
                        "opensky",
                    )
                )
                count += 1
        if count >= 3:
            break
    return out


async def fetch_restcountries_travel(settings: Settings) -> list[TravelConfirmation]:
    code = settings.ea_travel_home_country or "AE"
    data = await get_json(f"https://restcountries.com/v3.1/alpha/{code}")
    if not isinstance(data, list) or not data:
        return []
    c = data[0]
    name = c.get("name", {}).get("common", code)
    tz = (c.get("timezones") or ["UTC"])[0]
    capital = (c.get("capital") or ["—"])[0]
    return [
        TravelConfirmation(
            f"Home base: {name} ({capital})",
            "country_intel",
            None,
            tz,
            "restcountries",
        )
    ]


async def fetch_nominatim_travel(settings: Settings) -> list[TravelConfirmation]:
    city = settings.ea_weather_city or "Dubai"
    data = await get_json(
        "https://nominatim.openstreetmap.org/search",
        params={"q": city, "format": "json", "limit": 1},
        headers={"User-Agent": "Rudra/0.1 EA"},
    )
    if not isinstance(data, list) or not data:
        return []
    hit = data[0]
    return [
        TravelConfirmation(
            f"Geo: {hit.get('display_name', city)[:100]}",
            "geocode",
            None,
            hit.get("lat"),
            "nominatim",
        )
    ]
