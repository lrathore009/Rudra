# Integrations Foundation

Optional calendar and email intelligence. **The app starts without cloud credentials.**

## Providers

| Provider | Status |
|----------|--------|
| `mock_local` | Built-in demo data |
| `google_calendar` | Stub — connect later via env |
| `gmail` | Stub — connect later via env |

## APIs

- `GET /api/v1/integrations`
- `POST /api/v1/integrations/connect/mock`
- `GET /api/v1/calendar/events`
- `GET /api/v1/email/recent`
- `POST /api/v1/briefing/daily`

## Daily briefing

Combines:

- Calendar events (mock or future Google)
- Recent emails needing attention
- Project priorities and stale/blocked counts
- Suggested deep work block

Stored in `daily_briefings` and written to memory by the `morning_digest` scheduler job.

## HUD

**Daily Command Briefing** panel: connection status, meetings, flagged emails, generate briefing.

## Future env vars (optional)

```bash
GOOGLE_CALENDAR_CLIENT_ID=
GOOGLE_CALENDAR_CLIENT_SECRET=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
```

When unset, UI shows **Not connected** — no startup failure.
