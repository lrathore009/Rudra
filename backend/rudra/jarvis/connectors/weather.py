"""Open-Meteo weather — free, no API key."""

from __future__ import annotations

import httpx

from rudra.core.config import get_settings
from rudra.integrations.providers import WeatherSnapshot
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus


class WeatherConnector(BaseConnector):
    name = "weather"

    def __init__(self, session):
        self.session = session

    async def connect(self, user_id: str, **credentials) -> ConnectorStatus:
        city = credentials.get("city") or get_settings().ea_weather_city
        return ConnectorStatus("weather", True, f"Weather enabled for {city}")

    async def status(self, user_id: str) -> ConnectorStatus:
        return ConnectorStatus("weather", True, f"Open-Meteo · {get_settings().ea_weather_city}")

    async def snapshot(self, user_id: str) -> WeatherSnapshot | None:
        settings = get_settings()
        lat, lon = settings.ea_weather_lat, settings.ea_weather_lon
        city = settings.ea_weather_city
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                r = await client.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": "temperature_2m,weather_code,precipitation",
                        "timezone": "auto",
                    },
                )
                r.raise_for_status()
                cur = r.json().get("current", {})
                code = int(cur.get("weather_code", 0))
                summary = _weather_label(code)
                if cur.get("precipitation", 0) > 0:
                    summary += f", precipitation {cur['precipitation']}mm"
                return WeatherSnapshot(
                    location=city,
                    summary=summary,
                    temp_c=float(cur.get("temperature_2m", 0)),
                )
        except Exception:
            return WeatherSnapshot(city, "Weather unavailable", None, "open_meteo")


def _weather_label(code: int) -> str:
    if code == 0:
        return "Clear"
    if code in (1, 2, 3):
        return "Partly cloudy"
    if code in (51, 53, 55, 61, 63, 65):
        return "Rain"
    if code in (71, 73, 75):
        return "Snow"
    if code >= 95:
        return "Thunderstorm"
    return "Variable"
