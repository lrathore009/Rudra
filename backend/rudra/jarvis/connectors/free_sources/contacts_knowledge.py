"""Contacts and knowledge free sources — Wikidata, DBpedia, Gravatar, OpenAlex, Semantic Scholar, NASA, Eurostat."""

from __future__ import annotations

import hashlib

from rudra.core.config import Settings
from rudra.integrations.providers import CommandFeedItem, ContactRecord
from rudra.jarvis.connectors.free_sources._http import get_json, get_text


async def fetch_wikidata_contacts(settings: Settings) -> list[ContactRecord]:
    entities = [e.strip() for e in settings.ea_wikidata_entities.split(",") if e.strip()]
    if not entities:
        entities = ["Elon Musk", "Satya Nadella"]
    out: list[ContactRecord] = []
    for name in entities[:5]:
        data = await get_json(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": name,
                "language": "en",
                "format": "json",
                "limit": 1,
            },
        )
        if not isinstance(data, dict):
            continue
        hits = data.get("search", [])
        if not hits:
            continue
        desc = hits[0].get("description", "")
        out.append(ContactRecord(name, organization=desc[:80], role="public figure", provider="wikidata"))
    return out


async def fetch_dbpedia_contacts(settings: Settings) -> list[ContactRecord]:
    topics = [t.strip() for t in settings.ea_knowledge_topics.split(",") if t.strip()]
    if not topics:
        return []
    out: list[ContactRecord] = []
    for topic in topics[:2]:
        data = await get_json(
            "https://lookup.dbpedia.org/api/search",
            params={"query": topic, "format": "json", "maxResults": 2},
        )
        if not isinstance(data, dict):
            continue
        for doc in data.get("docs", [])[:2]:
            label = doc.get("label", topic)
            out.append(ContactRecord(label[:80], organization=topic, provider="dbpedia"))
    return out


async def fetch_gravatar_contacts(settings: Settings) -> list[ContactRecord]:
    user = settings.ea_imap_user or settings.owner_username
    if not user or "@" not in user:
        return []
    h = hashlib.md5(user.strip().lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    text = await get_text(url, timeout=5.0)
    if text is None:
        return []
    return [ContactRecord(user.split("@")[0].title(), email=user, provider="gravatar")]


async def fetch_openalex_intel(settings: Settings) -> list[CommandFeedItem]:
    topics = [t.strip() for t in settings.ea_knowledge_topics.split(",") if t.strip()]
    if not topics:
        topics = ["artificial intelligence"]
    out: list[CommandFeedItem] = []
    for topic in topics[:2]:
        data = await get_json(
            "https://api.openalex.org/works",
            params={"search": topic, "per_page": 3, "sort": "publication_date:desc"},
        )
        if not isinstance(data, dict):
            continue
        for work in data.get("results", [])[:3]:
            title = work.get("title") or topic
            out.append(
                CommandFeedItem(
                    "knowledge",
                    title[:120],
                    (work.get("abstract_inverted_index") and "Recent research") or topic,
                    "openalex",
                    work.get("id"),
                )
            )
    return out


async def fetch_semantic_scholar_intel(settings: Settings) -> list[CommandFeedItem]:
    topics = [t.strip() for t in settings.ea_knowledge_topics.split(",") if t.strip()]
    if not topics:
        return []
    data = await get_json(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": topics[0], "limit": 3, "fields": "title,year,abstract"},
    )
    if not isinstance(data, dict):
        return []
    return [
        CommandFeedItem(
            "knowledge",
            p.get("title", "Paper")[:120],
            (p.get("abstract") or "")[:200],
            "semantic_scholar",
            p.get("paperId"),
        )
        for p in data.get("data", [])[:3]
    ]


async def fetch_nasa_intel(settings: Settings) -> list[CommandFeedItem]:
    data = await get_json(
        "https://api.nasa.gov/planetary/apod",
        params={"api_key": settings.nasa_api_key or "DEMO_KEY"},
    )
    if not isinstance(data, dict) or data.get("media_type") != "image":
        return []
    return [
        CommandFeedItem(
            "knowledge",
            data.get("title", "NASA APOD")[:120],
            (data.get("explanation") or "")[:240],
            "nasa",
        )
    ]


async def fetch_eurostat_intel() -> list[CommandFeedItem]:
    data = await get_json(
        "https://ec.europa.eu/eurostat/api/discovery/tables",
        params={"lang": "en"},
        timeout=15.0,
    )
    if not isinstance(data, dict):
        return []
    tables = data.get("tables", [])[:3]
    return [
        CommandFeedItem(
            "knowledge",
            t.get("title", "Eurostat table")[:120],
            t.get("description", "")[:200],
            "eurostat",
            t.get("code"),
        )
        for t in tables
    ]


async def fetch_datagov_intel() -> list[CommandFeedItem]:
    data = await get_json(
        "https://catalog.data.gov/api/3/action/package_search",
        params={"q": "economy", "rows": 3},
        timeout=15.0,
    )
    if not isinstance(data, dict):
        return []
    results = data.get("result", {}).get("results", [])
    return [
        CommandFeedItem(
            "knowledge",
            r.get("title", "Dataset")[:120],
            (r.get("notes") or "")[:200],
            "data.gov",
            r.get("id"),
        )
        for r in results[:3]
    ]
