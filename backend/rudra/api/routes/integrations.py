"""Integration and briefing API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from rudra.api.deps import require_auth
from rudra.core.database import get_db
from rudra.integrations.executive import ExecutiveCommandService
from rudra.integrations.service import BriefingService, IntegrationService

router = APIRouter(tags=["integrations"])


class BriefingResponse(BaseModel):
    briefing_date: str
    content: str


class ConnectProviderRequest(BaseModel):
    provider: str
    refresh_token: str | None = None
    token_json: dict | None = None
    api_token: str | None = None
    api_key: str | None = None
    bot_token: str | None = None


class CsvImportRequest(BaseModel):
    kind: str = Field(description="finance | crm | health")
    csv_text: str


class TranscriptRequest(BaseModel):
    title: str
    content: str
    meeting_date: str | None = None
    provider: str = "manual"


@router.get("/integrations")
async def list_integrations(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await IntegrationService(db, user_id).list_integrations()


@router.post("/integrations/connect/mock")
async def connect_mock(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    integration = await IntegrationService(db, user_id).connect_mock()
    return {"provider": integration.provider, "status": integration.status}


@router.post("/integrations/connect")
async def connect_provider(
    body: ConnectProviderRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    svc = ExecutiveCommandService(db, user_id)
    creds = body.model_dump(exclude={"provider"}, exclude_none=True)
    return await svc.connect_provider(body.provider, **creds)


@router.post("/integrations/sync")
async def sync_integrations(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await ExecutiveCommandService(db, user_id).sync_all()


@router.get("/integrations/command-stack")
async def command_stack(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    return await ExecutiveCommandService(db, user_id).get_command_stack()


@router.post("/integrations/import/csv")
async def import_csv(
    body: CsvImportRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await ExecutiveCommandService(db, user_id).import_csv(body.kind, body.csv_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/integrations/transcripts")
async def add_transcript(
    body: TranscriptRequest,
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    row = await ExecutiveCommandService(db, user_id).add_transcript(
        body.title, body.content, meeting_date=body.meeting_date, provider=body.provider
    )
    return {
        "id": str(row.id),
        "title": row.title,
        "action_items": row.action_items or [],
    }


@router.get("/calendar/events")
async def calendar_events(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    events = await IntegrationService(db, user_id).calendar_events()
    return [
        {
            "title": e.title,
            "starts_at": e.starts_at,
            "ends_at": e.ends_at,
            "location": e.location,
            "provider": e.provider,
        }
        for e in events
    ]


@router.get("/email/recent")
async def recent_email(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    emails = await IntegrationService(db, user_id).recent_emails()
    return [
        {
            "sender": m.sender,
            "subject": m.subject,
            "snippet": m.snippet,
            "received_at": m.received_at,
            "needs_attention": m.needs_attention,
            "provider": m.provider,
        }
        for m in emails
    ]


@router.post("/briefing/daily", response_model=BriefingResponse)
async def daily_briefing(
    user_id: str = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    briefing = await BriefingService(db, user_id).generate_daily()
    return BriefingResponse(briefing_date=briefing.briefing_date, content=briefing.content)
