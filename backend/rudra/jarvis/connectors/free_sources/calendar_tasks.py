"""Calendar and task free sources — CalDAV/iCal, Todoist, GitHub, Trello, Hacker News."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from icalendar import Calendar

from rudra.core.config import Settings
from rudra.integrations.providers import CalendarEvent, TaskItem
from rudra.jarvis.connectors.free_sources._http import get_json, get_text


async def fetch_ical_events(settings: Settings) -> list[CalendarEvent]:
    urls = [u.strip() for u in settings.ea_caldav_urls.split(",") if u.strip()]
    if not urls:
        return []
    out: list[CalendarEvent] = []

    async def _one(url: str) -> None:
        text = await get_text(url, timeout=15.0)
        if not text:
            return
        try:
            cal = Calendar.from_ical(text)
            now = datetime.now()
            horizon = now + timedelta(days=14)
            for component in cal.walk():
                if component.name != "VEVENT":
                    continue
                summary = str(component.get("summary", "Event"))
                dtstart = component.get("dtstart")
                if not dtstart:
                    continue
                start = dtstart.dt
                if hasattr(start, "hour"):
                    start_dt = start
                else:
                    start_dt = datetime.combine(start, datetime.min.time())
                if start_dt.replace(tzinfo=None) < now - timedelta(days=1):
                    continue
                if start_dt.replace(tzinfo=None) > horizon:
                    continue
                dtend = component.get("dtend")
                end_s = None
                if dtend:
                    end = dtend.dt
                    end_s = end.strftime("%H:%M") if hasattr(end, "hour") else str(end)
                loc = str(component.get("location", "")) or None
                out.append(
                    CalendarEvent(
                        summary[:120],
                        start_dt.strftime("%Y-%m-%d %H:%M") if hasattr(start_dt, "hour") else str(start_dt),
                        end_s,
                        loc,
                        "caldav",
                    )
                )
        except Exception:
            return

    await asyncio.gather(*[_one(u) for u in urls[:5]])
    return out[:20]


async def fetch_todoist_tasks(settings: Settings, *, limit: int = 10) -> list[TaskItem]:
    token = settings.ea_todoist_token
    if not token:
        return []
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                "https://api.todoist.com/rest/v2/tasks",
                headers={"Authorization": f"Bearer {token.get_secret_value()}"},
            )
            if r.status_code != 200:
                return []
            return [
                TaskItem(
                    t.get("content", "Task")[:120],
                    "done" if t.get("is_completed") else "open",
                    t.get("due", {}).get("date") if isinstance(t.get("due"), dict) else None,
                    provider="todoist",
                    external_id=str(t.get("id")),
                )
                for t in r.json()[:limit]
            ]
    except Exception:
        return []


async def fetch_github_tasks(settings: Settings, *, limit: int = 10) -> list[TaskItem]:
    repos = [r.strip() for r in settings.ea_github_repos.split(",") if r.strip()]
    if not repos:
        return []
    token = settings.ea_github_token.get_secret_value() if settings.ea_github_token else None
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    out: list[TaskItem] = []
    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            for repo in repos[:3]:
                r = await client.get(
                    f"https://api.github.com/repos/{repo}/issues",
                    params={"state": "open", "per_page": 5},
                    headers=headers,
                )
                if r.status_code != 200:
                    continue
                for issue in r.json():
                    if "pull_request" in issue:
                        continue
                    out.append(
                        TaskItem(
                            issue.get("title", "Issue")[:120],
                            "open",
                            None,
                            repo,
                            "github",
                            external_id=str(issue.get("number")),
                        )
                    )
    except Exception:
        return []
    return out[:limit]


async def fetch_trello_tasks(settings: Settings, *, limit: int = 10) -> list[TaskItem]:
    key = settings.ea_trello_key
    token = settings.ea_trello_token
    board = settings.ea_trello_board_id
    if not (key and token and board):
        return []
    data = await get_json(
        f"https://api.trello.com/1/boards/{board}/cards",
        params={"key": key, "token": token.get_secret_value(), "fields": "name,due,url"},
    )
    if not isinstance(data, list):
        return []
    return [
        TaskItem(c.get("name", "Card")[:120], "open", c.get("due"), provider="trello", external_id=c.get("id"))
        for c in data[:limit]
    ]


async def fetch_hackernews_tasks(*, limit: int = 8) -> list[TaskItem]:
    ids = await get_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not isinstance(ids, list):
        return []
    out: list[TaskItem] = []

    async def _item(story_id: int) -> TaskItem | None:
        item = await get_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if not isinstance(item, dict):
            return None
        title = item.get("title", "")
        if not title:
            return None
        return TaskItem(
            title[:120],
            "open",
            None,
            "HN",
            "hackernews",
            external_id=str(story_id),
        )

    results = await asyncio.gather(*[_item(i) for i in ids[:limit]])
    for r in results:
        if r:
            out.append(r)
    return out
