"""RSS news headlines for morning briefing."""

from __future__ import annotations

import httpx
import xml.etree.ElementTree as ET

from rudra.core.config import get_settings
from rudra.integrations.providers import NewsHeadline
from rudra.jarvis.connectors.base import BaseConnector, ConnectorStatus


class NewsConnector(BaseConnector):
    name = "news"

    def __init__(self, session):
        self.session = session

    async def connect(self, user_id: str, **credentials) -> ConnectorStatus:
        return ConnectorStatus("news", True, "RSS feeds enabled")

    async def status(self, user_id: str) -> ConnectorStatus:
        feeds = get_settings().ea_news_feeds
        return ConnectorStatus("news", True, f"{len(feeds.split(','))} RSS feeds")

    async def headlines(self, user_id: str, *, limit: int = 5) -> list[NewsHeadline]:
        settings = get_settings()
        urls = [u.strip() for u in settings.ea_news_feeds.split(",") if u.strip()]
        out: list[NewsHeadline] = []
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            for url in urls:
                if len(out) >= limit:
                    break
                try:
                    r = await client.get(url)
                    r.raise_for_status()
                    root = ET.fromstring(r.text)
                    for item in root.findall(".//item")[:3]:
                        title = (item.findtext("title") or "").strip()
                        link = item.findtext("link")
                        if title:
                            out.append(NewsHeadline(title, url.split("/")[2], link))
                except Exception:
                    continue
        return out[:limit]
