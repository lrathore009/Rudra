/**
 * API client — browser uses same-origin proxy (/api/rudra → backend via app/api/rudra route).
 * Avoids CORS and mixed-content when the UI is on Vercel HTTPS and the backend is local/tunneled.
 */
import { authHeaders } from "./auth";
function apiBase(): string {
  if (typeof window !== "undefined") {
    return "/api/rudra";
  }
  return (
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.RUDRA_BACKEND_URL ||
    "http://localhost:8000/api"
  ).replace(/\/$/, "").replace(/\/api$/, "") + "/api";
}

const API_BASE = apiBase();

export interface CommandResponse {
  response: string;
  agent_type: string;
  agent_name: string;
  agent_intro: string;
  confidence: number;
  actions: Record<string, unknown>[];
  memories_created: string[];
  routing_analysis: RoutingAnalysisItem[];
  sources_used: Array<{ type: string; title: string; url?: string }>;
  voice_profile: VoiceProfile;
}

export interface RoutingAnalysisItem {
  agent: string;
  name: string;
  score: number;
  reason: string;
  selected: boolean;
}

export interface VoiceProfile {
  pitch?: number;
  rate?: number;
  voice_hints?: string[];
}

export interface AgentPhaseInfo {
  number: number;
  title: string;
  goal: string;
  status: "foundation" | "planned" | "in_progress" | "complete";
  foundation_complete?: boolean;
  deliverables?: string[];
  tools?: string[];
  hud?: string;
  depends_on?: string[];
}

export interface AgentInfo {
  type: string;
  name: string;
  description: string;
  data_sources?: string[];
  voice_profile?: VoiceProfile;
  phase?: AgentPhaseInfo;
}

export interface Memory {
  id: string;
  memory_type: string;
  title: string;
  content: string;
  summary: string | null;
  importance: number;
  created_at: string;
}

export interface ActStep {
  thought: string;
  tool: string | null;
  args: Record<string, unknown>;
  observation: string | null;
}

export interface ActResponse {
  answer: string;
  steps: ActStep[];
  tools_used: string[];
  model: string;
  latency_ms: number;
  completed: boolean;
}

export interface ToolInfo {
  name: string;
  description: string;
  parameters: Record<string, string>;
  safe: boolean;
}

export interface SkillInfo {
  name: string;
  description: string;
}

export interface SchedulerJob {
  id: string;
  name: string;
  enabled: boolean;
  interval_seconds: number | null;
  daily_at: string | null;
  last_run: number | null;
  next_run: number | null;
  last_result: string | null;
}

export interface TraceStats {
  count: number;
  success_rate?: number;
  avg_latency_ms?: number;
  p95_latency_ms?: number;
  avg_steps?: number;
  by_model?: Record<string, number>;
  top_tools?: Record<string, number>;
}

export interface ServiceHealth {
  service: string;
  ok: boolean;
  optional?: boolean;
  detail?: unknown;
  error?: string;
}

export interface ServicesHealth {
  status: string;
  required_ok: boolean;
  services: ServiceHealth[];
}

export interface GraphEntity {
  id: string;
  name: string;
  entity_type: string;
  description: string | null;
}

export interface GraphRelationship {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  relation_type: string;
  weight: number;
  notes: string | null;
}

export interface ProjectCard {
  id: string;
  name: string;
  status: string;
  priority: number;
  progress_percent: number;
  next_action: string | null;
  blockers: string | null;
  category: string | null;
}

export interface ProjectDashboard {
  projects: ProjectCard[];
  stale_count: number;
  blocked_count: number;
  weekly_briefing: string;
}

function friendlyFetchError(err: unknown): string {
  if (err instanceof Error && err.name === "AbortError") {
    return "Request timed out. Try localhost:3000 for long travel/research queries, or ask a shorter question.";
  }
  if (err instanceof TypeError && /fetch/i.test(err.message)) {
    return (
      "Cannot reach Rudra backend. On your Mac run: ./scripts/start.sh && ./scripts/start-tunnel.sh"
    );
  }
  if (err instanceof Error && err.message) return err.message;
  return "Backend unreachable — ensure start.sh and start-tunnel.sh are running on your Mac.";
}

async function getJSON<T>(path: string): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
    if (!res.ok) throw new Error(`${path} → ${res.status}`);
    return res.json() as Promise<T>;
  } catch (e) {
    throw new Error(friendlyFetchError(e));
  }
}

export async function executeCommand(
  command: string,
  agentType?: string
): Promise<CommandResponse> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 110_000);
  try {
    const res = await fetch(`${API_BASE}/v1/command`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ command, agent_type: agentType, auto_route: !agentType }),
      signal: controller.signal,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const body = await res.json();
        if (body?.detail) detail = body.detail;
      } catch {
        /* ignore */
      }
      throw new Error(detail);
    }
    return res.json();
  } catch (e) {
    throw new Error(friendlyFetchError(e));
  } finally {
    clearTimeout(timer);
  }
}

export async function agentAct(query: string, maxSteps?: number): Promise<ActResponse> {
  try {
    const res = await fetch(`${API_BASE}/v1/agent/act`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({ query, max_steps: maxSteps }),
    });
    if (!res.ok) throw new Error(`agent/act → ${res.status}`);
    return res.json();
  } catch (e) {
    throw new Error(friendlyFetchError(e));
  }
}

export interface StreamMeta {
  agent_type: string;
  agent_name: string;
  sources_used?: Array<{ type: string; title: string; url?: string }>;
}

/**
 * Streaming command over SSE. Tokens arrive incrementally; pass an AbortSignal to Stop.
 */
export async function streamCommand(
  command: string,
  opts: {
    agentType?: string;
    signal?: AbortSignal;
    onMeta?: (m: StreamMeta) => void;
    onToken: (text: string) => void;
    onDone?: (m: StreamMeta) => void;
  }
): Promise<void> {
  const res = await fetch(`${API_BASE}/v1/command/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ command, agent_type: opts.agentType, auto_route: !opts.agentType }),
    signal: opts.signal,
  });
  if (!res.ok || !res.body) throw new Error(`stream → ${res.status}`);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const frames = buf.split("\n\n");
    buf = frames.pop() ?? "";
    for (const frame of frames) {
      const line = frame.trim();
      if (!line.startsWith("data:")) continue;
      let data: { type?: string; text?: string } & Partial<StreamMeta>;
      try {
        data = JSON.parse(line.slice(5).trim());
      } catch {
        continue;
      }
      if (data.type === "token") opts.onToken(data.text ?? "");
      else if (data.type === "meta") opts.onMeta?.(data as StreamMeta);
      else if (data.type === "done") opts.onDone?.(data as StreamMeta);
    }
  }
}

export async function runSchedulerJob(jobId: string): Promise<{ job_id: string; result: string }> {
  const res = await fetch(`${API_BASE}/v1/scheduler/jobs/${jobId}/run`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`scheduler run → ${res.status}`);
  return res.json();
}

export const listAgents = () => getJSON<AgentInfo[]>("/v1/agents");
export const listSkills = () => getJSON<SkillInfo[]>("/v1/skills");
export const listTools = () => getJSON<ToolInfo[]>("/v1/agent/tools");
export const listMemories = (limit = 20) => getJSON<Memory[]>(`/v1/memories?limit=${limit}`);
export const listSchedulerJobs = () => getJSON<SchedulerJob[]>("/v1/scheduler/jobs");
export const traceStats = () => getJSON<TraceStats>("/v1/traces/stats");
export const healthServices = () => getJSON<ServicesHealth>("/v1/health/services");

export const listGraphEntities = (q?: string) =>
  getJSON<GraphEntity[]>(`/v1/graph/entities${q ? `?q=${encodeURIComponent(q)}` : ""}`);
export const getGraphEntity = (id: string) => getJSON<GraphEntity>(`/v1/graph/entities/${id}`);
export const getGraphEntityMemories = (id: string) =>
  getJSON<Memory[]>(`/v1/graph/entities/${id}/memories`);
export const listGraphRelationships = (entityId?: string) =>
  getJSON<GraphRelationship[]>(
    `/v1/graph/relationships${entityId ? `?entity_id=${entityId}` : ""}`
  );

export const getProjectDashboard = () => getJSON<ProjectDashboard>("/v1/projects/dashboard");
export const listProjects = () => getJSON<ProjectCard[]>("/v1/projects");

export interface DocumentRecord {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  page_count: number | null;
  char_count: number | null;
  summary: string | null;
  error_message: string | null;
}

export async function uploadDocument(file: File): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/v1/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!res.ok) throw new Error(`upload → ${res.status}`);
  return res.json() as Promise<DocumentRecord>;
}

export const listDocuments = () => getJSON<DocumentRecord[]>("/v1/documents");

export async function askDocument(query: string, documentId?: string) {
  const res = await fetch(`${API_BASE}/v1/documents/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ query, document_id: documentId }),
  });
  if (!res.ok) throw new Error(`documents/ask → ${res.status}`);
  return res.json() as Promise<{ answer: string; citations: Array<Record<string, unknown>> }>;
}

export interface IntegrationStatus {
  provider: string;
  connected: boolean;
  detail: string;
  tier?: number;
  status?: string;
}

export interface CalendarEvent {
  title: string;
  starts_at: string;
  ends_at: string | null;
  location: string | null;
  provider: string;
}

export interface EmailMessage {
  sender: string;
  subject: string;
  snippet: string | null;
  received_at: string;
  needs_attention: boolean;
  provider: string;
}

export interface BriefingPayload {
  briefing_date: string;
  content: string;
}

export const listIntegrations = () => getJSON<IntegrationStatus[]>("/v1/integrations");
export const connectMockIntegration = () =>
  fetch(`${API_BASE}/v1/integrations/connect/mock`, { method: "POST", headers: authHeaders() }).then(
    (r) => {
      if (!r.ok) throw new Error("connect mock failed");
      return r.json();
    }
  );
export const syncExecutiveSources = () =>
  fetch(`${API_BASE}/v1/integrations/sync`, { method: "POST", headers: authHeaders() }).then((r) => {
    if (!r.ok) throw new Error("sync failed");
    return r.json() as Promise<Record<string, number>>;
  });
export const getCommandStack = () =>
  getJSON<Record<string, unknown>>("/v1/integrations/command-stack");
export const connectProvider = (provider: string, credentials: Record<string, string> = {}) =>
  fetch(`${API_BASE}/v1/integrations/connect`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ provider, ...credentials }),
  }).then((r) => {
    if (!r.ok) throw new Error(`connect ${provider} failed`);
    return r.json();
  });
export const listCalendarEvents = () => getJSON<CalendarEvent[]>("/v1/calendar/events");
export const listRecentEmails = () => getJSON<EmailMessage[]>("/v1/email/recent");
export async function generateDailyBriefing() {
  const res = await fetch(`${API_BASE}/v1/briefing/daily`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`briefing → ${res.status}`);
  return res.json() as Promise<BriefingPayload>;
}

export interface SpokenDigestPayload {
  text: string;
  sources_preview?: string;
  audio?: { mode: string; text?: string; mime?: string };
}

export async function generateSpokenDigest() {
  const res = await fetch(`${API_BASE}/v1/jarvis/digest/spoken`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`spoken digest → ${res.status}`);
  return res.json() as Promise<SpokenDigestPayload>;
}

export const getJarvisConfig = () => getJSON<Record<string, unknown>>("/v1/jarvis/config");
export const listJarvisConnectors = () =>
  getJSON<{ provider: string; connected: boolean; detail: string }[]>("/v1/jarvis/connectors");
export const listJarvisOperators = () =>
  getJSON<{ id: string; name: string; description: string }[]>("/v1/jarvis/operators");
export const getRoutingHints = () => getJSON<Record<string, unknown>>("/v1/jarvis/learning/routing-hints");

export interface ResearchReportSummary {
  id: string;
  title: string;
  confidence_score: number;
  query?: string;
  created_at?: string | null;
  topic_tags?: string[];
  score?: number;
  snippet?: string;
}

export interface ResearchLibraryPayload {
  reports: ResearchReportSummary[];
  trends: {
    count: number;
    avg_confidence: number;
    stale_count: number;
    weekly?: Array<{ week: string; avg_confidence: number; count: number }>;
  };
  watchlist: Array<{ id: string; topic: string; query_template: string; ttl_days: number }>;
}

export async function getResearchLibrary(limit = 12) {
  const res = await fetch(`${API_BASE}/v1/research/library?limit=${limit}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`research/library → ${res.status}`);
  return res.json() as Promise<ResearchLibraryPayload>;
}

export async function searchResearchLibrary(query: string, limit = 8) {
  const res = await fetch(`${API_BASE}/v1/research/library/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ query, limit, hybrid: true }),
  });
  if (!res.ok) throw new Error(`research/search → ${res.status}`);
  return res.json() as Promise<ResearchReportSummary[]>;
}

export async function addResearchWatchlist(topic: string, queryTemplate: string, ttlDays = 30) {
  const res = await fetch(`${API_BASE}/v1/research/watchlist`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ topic, query_template: queryTemplate, ttl_days: ttlDays }),
  });
  if (!res.ok) throw new Error(`research/watchlist → ${res.status}`);
  return res.json() as Promise<{ id: string; topic: string }>;
}

export async function generateSpokenResearchBrief(topic?: string) {
  const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
  const res = await fetch(`${API_BASE}/v1/jarvis/research/spoken${qs}`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(`spoken research → ${res.status}`);
  return res.json() as Promise<SpokenDigestPayload & { trends?: Record<string, unknown> }>;
}

export interface DomainRequest {
  id: string;
  title: string;
  status: string;
  venue_name?: string | null;
}

export interface DomainTrip {
  id: string;
  title: string;
  status: string;
  legs?: Array<{ destination: string; status: string }>;
}

export interface DomainDraft {
  id: string;
  title: string;
  status: string;
  version: number;
}

export interface DomainDeck {
  id: string;
  title: string;
  slides: number;
  status: string;
}

export async function librarianSearch(query: string) {
  const res = await fetch(`${API_BASE}/v1/domains/librarian/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ query, limit: 8 }),
  });
  if (!res.ok) throw new Error(`librarian search → ${res.status}`);
  return res.json() as Promise<Array<{ type: string; title: string; snippet?: string; score?: number }>>;
}

export const getConciergeRequests = () => getJSON<DomainRequest[]>("/v1/domains/concierge/requests");
export async function createConciergeRequest(title: string, details: string) {
  const res = await fetch(`${API_BASE}/v1/domains/concierge/requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ title, details }),
  });
  if (!res.ok) throw new Error("concierge create failed");
  return res.json();
}

export const getTravelTrips = () => getJSON<DomainTrip[]>("/v1/domains/travel/trips");
export async function createTrip(title: string, destinations: string[]) {
  const res = await fetch(`${API_BASE}/v1/domains/travel/trips`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ title, destinations }),
  });
  if (!res.ok) throw new Error("trip create failed");
  return res.json();
}

export const getLuxuryDesk = () => getJSON<{ trends: { count: number; avg_exclusivity: number }; snapshots: unknown[] }>("/v1/domains/luxury/desk");
export const getWritingDrafts = () => getJSON<DomainDraft[]>("/v1/domains/writing/drafts");
export const getPresentationDecks = () => getJSON<DomainDeck[]>("/v1/domains/presentation/decks");
export const getOpsRunbook = () =>
  getJSON<{ maintenance_due: Array<{ title: string; next_due: string }>; vendor_count: number }>(
    "/v1/domains/operations/runbook"
  );

export async function buildDeck(title: string, query: string) {
  const res = await fetch(`${API_BASE}/v1/domains/presentation/decks/build`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ title, query, slides: 6 }),
  });
  if (!res.ok) throw new Error("deck build failed");
  return res.json();
}

export async function checkHealth() {
  try {
    return await getJSON<{ status: string }>("/v1/health");
  } catch {
    return { status: "offline" };
  }
}
