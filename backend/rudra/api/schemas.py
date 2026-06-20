"""Pydantic schemas for API request/response models."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# --- Memory ---
class MemoryCreate(BaseModel):
    memory_type: str
    title: str
    content: str
    summary: str | None = None
    importance: float = 0.5
    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None


class MemoryResponse(BaseModel):
    id: UUID
    memory_type: str
    title: str
    content: str
    summary: str | None
    importance: float
    source: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MemorySearchRequest(BaseModel):
    query: str
    memory_type: str | None = None
    limit: int = 10


# --- Agents ---
class AgentInvokeRequest(BaseModel):
    query: str
    agent_type: str | None = None
    session_id: str | None = None


class AgentResponse(BaseModel):
    agent_type: str
    content: str
    confidence: float
    citations: list[dict[str, str]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)


class AgentPhaseInfo(BaseModel):
    number: int
    title: str
    goal: str
    status: str
    foundation_complete: bool = True
    deliverables: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    hud: str = ""
    depends_on: list[str] = Field(default_factory=list)


class AgentInfo(BaseModel):
    type: str
    name: str
    description: str
    data_sources: list[str] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    phase: AgentPhaseInfo | None = None


class RoutingAnalysisItem(BaseModel):
    agent: str
    name: str
    score: float
    reason: str
    selected: bool = False


# --- Research ---
class ResearchRequest(BaseModel):
    query: str
    sources: list[str] | None = None
    max_sources: int = 10


class ResearchResponse(BaseModel):
    query: str
    summary: str
    findings: list[str]
    confidence_score: float
    citations: list[dict[str, str]]
    source_count: int
    report_id: str | None = None
    from_library: bool = False


# --- Luxury ---
class LuxuryResearchRequest(BaseModel):
    subject: str
    category: str
    depth: str = "standard"


class LuxuryIntelligenceResponse(BaseModel):
    category: str
    subject: str
    briefing: str
    key_facts: list[str]
    exclusivity_score: float
    investment_relevance: float
    sources: list[dict[str, str]]


# --- Workflows ---
class WorkflowCreateRequest(BaseModel):
    name: str
    description: str = ""
    steps: list[dict[str, Any]]


class WorkflowResponse(BaseModel):
    id: str
    name: str
    status: str
    steps: list[dict[str, Any]]


# --- System ---
class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


class ServicesHealthResponse(BaseModel):
    status: str
    required_ok: bool
    services: list[dict[str, Any]]


class CommandRequest(BaseModel):
    """Primary command interface — Rudra's main input."""
    command: str
    context: dict[str, Any] = Field(default_factory=dict)
    agent_type: str | None = None
    auto_route: bool = True


class CommandResponse(BaseModel):
    response: str
    agent_type: str
    agent_name: str = ""
    agent_intro: str = ""
    confidence: float
    actions: list[dict[str, Any]] = Field(default_factory=list)
    memories_created: list[str] = Field(default_factory=list)
    routing_analysis: list[RoutingAnalysisItem] = Field(default_factory=list)
    sources_used: list[dict[str, str]] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
