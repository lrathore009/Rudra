"""News and world-context free APIs — GDELT, Guardian, NewsAPI, Mediastack, Reddit."""

from __future__ import annotations

from rudra.core.config import Settings
from rudra.integrations.providers import NewsHeadline
from rudra.jarvis.connectors.free_sources._http import get_json


async def fetch_gdelt_headlines(*, limit: int = 5) -> list[NewsHeadline]:
    data = await get_json(
        "https://api.gdeltproject.org/api/v2/doc/doc",
        params={
            "query": "business OR economy OR technology",
            "mode": "artlist",
            "maxrecords": limit,
            "format": "json",
        },
        timeout=15.0,
    )
    if not isinstance(data, dict):
        return []
    articles = data.get("articles", [])
    return [
        NewsHeadline(
            a.get("title", "Event")[:140],
            a.get("domain", "GDELT"),
            a.get("url"),
        )
        for a in articles[:limit]
        if a.get("title")
    ]


async def fetch_guardian_headlines(settings: Settings, *, limit: int = 5) -> list[NewsHeadline]:
    key = settings.guardian_api_key
    if not key:
        return []
    data = await get_json(
        "https://content.guardianapis.com/search",
        params={
            "api-key": key.get_secret_value(),
            "section": "business",
            "page-size": limit,
            "order-by": "newest",
        },
    )
    if not isinstance(data, dict):
        return []
    results = data.get("response", {}).get("results", [])
    return [
        NewsHeadline(r.get("webTitle", "")[:140], "The Guardian", r.get("webUrl"))
        for r in results[:limit]
    ]


async def fetch_newsapi_headlines(settings: Settings, *, limit: int = 5) -> list[NewsHeadline]:
    key = settings.newsapi_key
    if not key:
        return []
    data = await get_json(
        "https://newsapi.org/v2/top-headlines",
        params={"apiKey": key.get_secret_value(), "category": "business", "pageSize": limit},
    )
    if not isinstance(data, dict):
        return []
    return [
        NewsHeadline(a.get("title", "")[:140], a.get("source", {}).get("name", "NewsAPI"), a.get("url"))
        for a in data.get("articles", [])[:limit]
        if a.get("title")
    ]


async def fetch_mediastack_headlines(settings: Settings, *, limit: int = 5) -> list[NewsHeadline]:
    key = settings.mediastack_api_key
    if not key:
        return []
    data = await get_json(
        "http://api.mediastack.com/v1/news",
        params={"access_key": key.get_secret_value(), "categories": "business", "limit": limit},
    )
    if not isinstance(data, dict):
        return []
    return [
        NewsHeadline(a.get("title", "")[:140], a.get("source", "Mediastack"), a.get("url"))
        for a in data.get("data", [])[:limit]
        if a.get("title")
    ]


async def fetch_reddit_headlines(settings: Settings, *, limit: int = 5) -> list[NewsHeadline]:
    subs = [s.strip() for s in settings.ea_reddit_subreddits.split(",") if s.strip()]
    out: list[NewsHeadline] = []
    for sub in subs[:3]:
        data = await get_json(
            f"https://www.reddit.com/r/{sub}/hot.json",
            params={"limit": 3},
            headers={"User-Agent": "Rudra/0.1 EA"},
        )
        if not isinstance(data, dict):
            continue
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            title = post.get("title")
            if title:
                out.append(
                    NewsHeadline(
                        title[:140],
                        f"r/{sub}",
                        f"https://reddit.com{post.get('permalink', '')}",
                    )
                )
        if len(out) >= limit:
            break
    return out[:limit]
