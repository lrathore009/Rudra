# Rudra Development Roadmap

## Founder OS upgrade (2026-06) — COMPLETE

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | JWT auth, rate limits, login HUD, audit | ✅ |
| 2 | Knowledge graph + extraction + HUD | ✅ |
| 3 | Project OS + dashboard + agent context | ✅ |
| 4 | Document brain + tools + HUD | ✅ |
| 5 | Mock calendar/email + daily briefing | ✅ |

See `docs/SECURITY.md`, `docs/KNOWLEDGE_GRAPH.md`, `docs/PROJECT_OS.md`, `docs/DOCUMENT_BRAIN.md`, `docs/INTEGRATIONS.md`.

---

## Agent phases (2026-06) — COMPLETE

Nine specialist upgrade tracks — one phase per agent. Each phase ships encoded domain data, context enrichment, ReAct tools, and a skill.

| Phase | Agent | Title | Status |
|-------|-------|-------|--------|
| 1 | Executive Assistant | Executive Command Center | ✅ |
| 2 | Research Analyst | Research Library | ✅ |
| 3 | Concierge Specialist | Experience Concierge | ✅ |
| 4 | Luxury Intelligence Analyst | Luxury Market Desk | ✅ |
| 5 | Travel Specialist | Itinerary Engine | ✅ |
| 6 | Knowledge Librarian | Unified Retrieval | ✅ |
| 7 | Writing Assistant | Voice & Draft Studio | ✅ |
| 8 | Presentation Builder | Deck Builder | ✅ |
| 9 | Personal Operations Manager | Operations Runbook | ✅ |

See `docs/AGENT_PHASES.md` for full deliverables, tools, and dependencies.

---

Five-phase plan from MVP to full personal intelligence ecosystem.

---

## Phase 1: MVP (Months 1–3)

**Goal:** Functional personal intelligence command center with core memory, agents, and research.

### Features

- [x] Command center web UI (Bloomberg Terminal aesthetic)
- [x] 9 specialized agents with auto-routing
- [x] Multi-model brain (OpenAI, Anthropic, Ollama)
- [x] 6 memory types with PostgreSQL + pgvector
- [x] Research engine with web search and credibility scoring
- [x] Luxury intelligence module (10 categories)
- [x] WebSocket real-time commands
- [x] Audit logging foundation
- [x] Docker Compose local development
- [ ] Embedding generation pipeline
- [ ] Semantic memory search (UI)

### Architecture

```
Web (Next.js) → FastAPI → PostgreSQL + Qdrant + Redis
                ↓
         Brain + Agents + Research + Memory
```

Single-server deployment. No auth (single-user MVP). Local Docker stack.

### Folder Structure

```
Rudra/
├── backend/rudra/          # Python FastAPI application
│   ├── brain/              # Multi-model orchestrator
│   ├── memory/             # Memory layer
│   ├── agents/             # 9 specialized agents
│   ├── research/           # Research engine
│   ├── knowledge/          # Luxury intelligence
│   ├── workflows/          # Workflow engine
│   ├── voice/              # Voice stub
│   ├── security/           # Encryption + audit
│   └── api/                # REST + WebSocket routes
├── frontend/src/           # Next.js command center
├── infrastructure/         # Docker, K8s (future)
├── docs/                   # Architecture + roadmap
└── scripts/                # Dev setup
```

### Database Schema

Tables: `memories`, `memory_tags`, `memory_links`, `projects`, `preferences`, `relationships`, `research_reports`, `audit_logs`.

Vector dimension: 1536 (OpenAI ada-002 compatible).

### APIs

| Endpoint | Status |
|----------|--------|
| POST `/api/v1/command` | ✅ |
| GET `/api/v1/agents` | ✅ |
| POST `/api/v1/agents/invoke` | ✅ |
| CRUD `/api/v1/memories` | ✅ |
| POST `/api/v1/research` | ✅ |
| POST `/api/v1/luxury/research` | ✅ |
| GET `/api/v1/luxury/trends` | ✅ |
| WS `/ws` | ✅ |

### Security Design

- AES-256 encryption service (Fernet)
- JWT token infrastructure (not enforced in MVP)
- Immutable audit logs on memory operations
- Environment-based secret management
- CORS restricted to localhost

### Deployment Strategy

```bash
docker compose up -d          # Infrastructure
cd backend && uvicorn ...     # API server
cd frontend && npm run dev    # Web UI
```

Single machine. No Kubernetes. Data volumes persisted locally.

### Cost Estimates (Monthly)

| Item | Cost |
|------|------|
| Local hardware | $0 (existing) |
| OpenAI API (moderate use) | $50–150 |
| Anthropic API | $30–100 |
| Tavily search | $0–50 |
| Cloud hosting (optional) | $0 (local-first) |
| **Total** | **$80–300/mo** |

### Risks

| Risk | Mitigation |
|------|-----------|
| API key exposure | .env gitignored; encrypted vault in Phase 2 |
| Memory without embeddings | Embedding pipeline in Phase 1 completion |
| Single point of failure | Docker health checks; backup scripts |
| Model provider outage | Multi-model failover already implemented |

### Testing Strategy

- Unit tests: brain routing, memory CRUD, credibility scoring
- Integration tests: command → agent → memory flow
- API tests: pytest + httpx against FastAPI TestClient
- Manual: command center UI smoke tests

---

## Phase 2: Beta (Months 4–6)

**Goal:** Production-quality security, voice, autonomous research, and semantic search.

### Features

- Full authentication (JWT + biometric on mobile)
- End-to-end encryption for memory content
- Embedding pipeline (OpenAI + local fallback)
- Semantic memory search with relevance ranking
- Voice layer: wake word, STT, TTS
- Autonomous research scheduling (Celery + Redis)
- Academic paper search (Semantic Scholar API)
- News aggregation (NewsAPI)
- Workflow engine with approval UI
- Knowledge graph visualization
- Qdrant vector search integration
- Kubernetes manifests
- Automated backups with encryption

### Architecture

```
                    ┌── Celery Workers (research, embeddings)
                    │
Clients ──▶ API ────┼── PostgreSQL (primary)
                    ├── Qdrant (vectors)
                    ├── Redis (queue + cache)
                    └── Ollama (local inference)
```

Multi-container Docker Compose. Optional K8s for cloud deployment.

### Folder Structure (Additions)

```
backend/rudra/
├── embeddings/         # Embedding generation pipeline
├── tasks/              # Celery background tasks
├── auth/               # Authentication module
└── graph/              # Knowledge graph operations

frontend/src/
├── components/graph/   # Knowledge graph viz
├── components/voice/   # Voice UI
└── app/settings/       # User preferences

infrastructure/
├── k8s/                # Kubernetes manifests
│   ├── backend/
│   ├── frontend/
│   ├── postgres/
│   └── qdrant/
└── backup/             # Encrypted backup scripts
```

### Database Schema (Additions)

```sql
-- New tables
users (id, email, password_hash, encryption_salt, created_at)
sessions (id, user_id, token_hash, expires_at)
scheduled_tasks (id, user_id, cron, task_type, config, last_run)
embeddings_queue (id, memory_id, status, model, created_at)
voice_sessions (id, user_id, transcript, state, created_at)
```

Migration: `002_auth_and_embeddings.py`

### APIs (Additions)

| Endpoint | Purpose |
|----------|---------|
| POST `/api/v1/auth/login` | Authentication |
| POST `/api/v1/memories/search` | Semantic search |
| POST `/api/v1/voice/transcribe` | Speech-to-text |
| POST `/api/v1/voice/synthesize` | Text-to-speech |
| GET/POST `/api/v1/workflows` | Workflow management |
| GET `/api/v1/graph` | Knowledge graph |
| POST `/api/v1/tasks/schedule` | Autonomous research |

### Security Design

- User-derived encryption keys (PBKDF2, 600K iterations)
- Memory content encrypted before storage
- API keys in encrypted vault table
- Rate limiting (Redis-backed)
- Session management with refresh tokens
- Audit log integrity checksums

### Deployment Strategy

```bash
# Local
docker compose -f docker-compose.yml -f docker-compose.prod.yml up

# Cloud (optional)
kubectl apply -f infrastructure/k8s/
```

Helm chart for one-command deployment. TLS via cert-manager.

### Cost Estimates (Monthly)

| Item | Cost |
|------|------|
| AI APIs (increased usage) | $150–400 |
| Cloud VPS (4 vCPU, 16GB) | $40–80 |
| Tavily + NewsAPI + Semantic Scholar | $50–100 |
| ElevenLabs + Deepgram (voice) | $30–80 |
| Domain + TLS | $15 |
| **Total** | **$285–675/mo** |

### Risks

| Risk | Mitigation |
|------|-----------|
| Voice latency | Local STT fallback (Whisper) |
| Embedding cost at scale | Batch processing; local model option |
| K8s complexity | Docker Compose remains primary for single-user |
| Key loss = data loss | Recovery key export flow |

### Testing Strategy

- Encryption round-trip tests
- Voice pipeline latency benchmarks
- Semantic search recall@k evaluation
- Load testing: 100 concurrent commands
- Security audit (OWASP top 10)
- Backup/restore verification

---

## Phase 3: Personal Production (Months 7–12)

**Goal:** Daily-driver personal OS across web, desktop, and mobile.

### Features

- Tauri desktop app (macOS, Windows, Linux)
- React Native mobile app (iOS, Android)
- Offline mode with sync queue
- Calendar integration (Google, Apple)
- Email triage and drafting
- Document ingestion (PDF, DOCX → memory)
- Preference learning (automatic from interactions)
- Relationship intelligence (CRM-lite)
- Project tracking with memory context
- Daily/weekly automated briefings
- Custom agent creation
- Data export (full user data portability)
- Multi-device sync with conflict resolution

### Architecture

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Desktop  │  │  Mobile  │  │   Web    │
│  Tauri   │  │   Expo   │  │ Next.js  │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     └──────────────┴──────────────┘
                    │
              Sync Gateway
                    │
              Rudra Backend
         (local or self-hosted cloud)
```

Local-first with optional cloud sync relay (user-controlled).

### Folder Structure (Additions)

```
desktop/                  # Tauri application
├── src-tauri/
└── src/

mobile/                   # React Native / Expo
├── app/
└── components/

backend/rudra/
├── integrations/         # Calendar, email, documents
├── sync/                 # Multi-device sync engine
├── learning/             # Preference extraction
└── briefings/            # Automated briefing generator

packages/
└── shared/               # Shared types and utilities
```

### Database Schema (Additions)

```sql
devices (id, user_id, name, platform, last_sync, push_token)
sync_log (id, device_id, entity_type, entity_id, operation, timestamp)
integrations (id, user_id, provider, credentials_encrypted, config)
documents (id, user_id, filename, content_hash, extracted_text, memory_ids)
briefings (id, user_id, type, content, scheduled_at, delivered_at)
```

### APIs (Additions)

| Endpoint | Purpose |
|----------|---------|
| POST `/api/v1/sync/push` | Device sync upload |
| GET `/api/v1/sync/pull` | Device sync download |
| POST `/api/v1/integrations/connect` | OAuth integrations |
| POST `/api/v1/documents/ingest` | Document processing |
| GET `/api/v1/briefings/latest` | Latest briefing |
| POST `/api/v1/export` | Full data export |
| DELETE `/api/v1/account/purge` | Complete data deletion |

### Security Design

- Device-specific encryption keys
- Sync encrypted in transit (TLS) and at rest
- Integration OAuth tokens in encrypted vault
- Document content never sent to third parties without consent
- Per-device audit trail
- Recovery phrase for key restoration

### Deployment Strategy

- **Primary:** Local server (Mac Mini / NUC / home server)
- **Secondary:** Self-hosted VPS with WireGuard VPN
- **Sync relay:** Optional encrypted relay (no plaintext access)
- Desktop/mobile connect to local IP or VPN

### Cost Estimates (Monthly)

| Item | Cost |
|------|------|
| AI APIs (daily driver usage) | $200–600 |
| Home server electricity | $5–15 |
| Cloud relay (optional) | $20–40 |
| Apple Developer + Google Play | ~$8/mo amortized |
| Integration APIs | $0–50 |
| **Total** | **$233–713/mo** |

### Risks

| Risk | Mitigation |
|------|-----------|
| Sync conflicts | CRDT-based conflict resolution |
| Offline complexity | Queue-based sync with retry |
| App store review | Privacy-first positioning; no data collection |
| Integration API changes | Adapter pattern; graceful degradation |

### Testing Strategy

- Cross-platform E2E (Playwright + Detox)
- Sync conflict simulation
- Offline → online transition tests
- Document ingestion accuracy tests
- Briefing quality evaluation (human review)
- Battery/performance profiling on mobile

---

## Phase 4: Advanced Automation (Months 13–18)

**Goal:** Autonomous intelligence that anticipates needs and executes complex workflows.

### Features

- Proactive intelligence (unsolicited briefings, alerts)
- Multi-step autonomous workflows with approval gates
- Agent collaboration (research → writing → presentation pipeline)
- Financial intelligence (portfolio awareness, market alerts)
- Travel automation (monitor prices, book on approval)
- Luxury deal monitoring (auctions, openings, exclusives)
- Smart home integration (Phase 4+ optional)
- Custom workflow builder (visual)
- Agent memory specialization (per-agent knowledge bases)
- Confidence-calibrated auto-actions
- Research subscription feeds
- Natural language workflow creation

### Architecture

```
┌─────────────────────────────────────────┐
│           Autonomous Engine              │
│  ┌─────────┐  ┌──────────┐  ┌────────┐ │
│  │ Scheduler│  │ Workflow │  │ Monitor│ │
│  │ (Cron)  │  │ Executor │  │ (Alerts)│ │
│  └────┬────┘  └────┬─────┘  └───┬────┘ │
│       └────────────┼────────────┘       │
│                    ▼                    │
│            Agent Orchestrator           │
│         (multi-agent collaboration)     │
└─────────────────────────────────────────┘
```

Event-driven architecture with Redis Streams.

### Folder Structure (Additions)

```
backend/rudra/
├── autonomous/           # Proactive intelligence engine
├── monitors/             # Price, news, luxury deal monitors
├── pipelines/            # Multi-agent pipelines
└── approvals/            # Human-in-the-loop approval system

frontend/src/
├── app/workflows/        # Visual workflow builder
├── app/approvals/        # Approval queue UI
└── components/pipelines/ # Pipeline visualization
```

### Database Schema (Additions)

```sql
monitors (id, user_id, type, config, last_check, active)
pipeline_runs (id, pipeline_id, status, steps_json, started_at, completed_at)
approvals (id, user_id, action_type, payload, status, expires_at)
auto_actions (id, user_id, trigger, action, confidence_threshold, enabled)
subscriptions (id, user_id, topic, frequency, last_delivered)
```

### APIs (Additions)

| Endpoint | Purpose |
|----------|---------|
| CRUD `/api/v1/monitors` | Monitor management |
| CRUD `/api/v1/pipelines` | Pipeline definitions |
| GET `/api/v1/approvals/pending` | Approval queue |
| POST `/api/v1/approvals/{id}/decide` | Approve/reject |
| GET `/api/v1/proactive/feed` | Proactive intelligence feed |
| POST `/api/v1/pipelines/execute` | Run pipeline |

### Security Design

- All autonomous actions require confidence threshold
- Financial/booking actions always require explicit approval
- Autonomous action audit trail with rollback capability
- Rate limits on auto-actions (max per hour/day)
- Kill switch for all automation

### Deployment Strategy

- Dedicated worker nodes for autonomous engine
- Redis Streams for event processing
- Separate monitoring container
- Prometheus + Grafana for observability

### Cost Estimates (Monthly)

| Item | Cost |
|------|------|
| AI APIs (autonomous usage) | $400–1,000 |
| Infrastructure | $50–100 |
| External data feeds | $100–300 |
| Monitor API costs | $50–100 |
| **Total** | **$600–1,500/mo** |

### Risks

| Risk | Mitigation |
|------|-----------|
| Autonomous errors | Confidence thresholds; approval gates |
| Runaway API costs | Budget caps; rate limiting |
| Stale monitors | Health checks; auto-disable on failure |
| Over-automation | User controls granularity per action type |

### Testing Strategy

- Pipeline integration tests (multi-agent)
- Approval flow E2E tests
- Monitor accuracy validation
- Cost simulation (API usage projection)
- Chaos testing (provider failures during automation)
- Human evaluation of proactive intelligence quality

---

## Phase 5: Rudra Ecosystem (Months 19–36)

**Goal:** Complete personal intelligence platform with ecosystem extensibility.

### Features

- Plugin system for custom agents and integrations
- Rudra SDK for third-party extensions
- Shared intelligence modules (opt-in, encrypted)
- Multi-modal input (images, documents, video analysis)
- AR/voice-first mobile experience
- Family/office mode (controlled sharing)
- Legacy mode (knowledge preservation planning)
- Advanced knowledge graph reasoning
- Predictive intelligence (pattern-based anticipation)
- Custom model fine-tuning on user data (local)
- Federation protocol (Rudra-to-Rudra encrypted sharing)
- Marketplace for agent templates

### Architecture

```
┌──────────────────────────────────────────────┐
│              Rudra Ecosystem                  │
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │ Plugin  │  │   SDK    │  │ Marketplace │ │
│  │ Runtime │  │  (API)   │  │  (Agents)   │ │
│  └────┬────┘  └────┬─────┘  └──────┬──────┘ │
│       └─────────────┼───────────────┘        │
│                     ▼                         │
│           Rudra Core Platform                 │
│    (Brain + Memory + Agents + Security)       │
│                     │                         │
│       ┌─────────────┼─────────────┐          │
│       ▼             ▼             ▼          │
│   Local Model   Cloud Relay   Federation     │
│   Fine-tuning   (optional)    Protocol       │
└──────────────────────────────────────────────┘
```

### Folder Structure (Additions)

```
sdk/                      # Rudra SDK (Python + TypeScript)
├── python/
└── typescript/

plugins/                  # Plugin runtime and examples
├── runtime/
└── examples/

marketplace/              # Agent template registry
├── registry/
└── templates/

backend/rudra/
├── plugins/              # Plugin loader and sandbox
├── federation/           # Encrypted Rudra-to-Rudra protocol
├── finetuning/           # Local model fine-tuning pipeline
└── multimodal/           # Image, video, document analysis
```

### Database Schema (Additions)

```sql
plugins (id, user_id, name, version, manifest, enabled, sandbox_config)
federation_peers (id, user_id, peer_id, public_key, trust_level)
model_versions (id, user_id, base_model, fine_tuned_path, metrics)
shared_modules (id, owner_id, module_type, encrypted_content, access_list)
legacy_plans (id, user_id, plan_config, trustees, activated)
```

### APIs (Additions)

| Endpoint | Purpose |
|----------|---------|
| CRUD `/api/v1/plugins` | Plugin management |
| POST `/api/v1/plugins/{id}/execute` | Run plugin |
| GET `/api/v1/marketplace` | Browse agent templates |
| POST `/api/v1/federation/share` | Encrypted sharing |
| POST `/api/v1/models/finetune` | Start fine-tuning |
| POST `/api/v1/multimodal/analyze` | Multi-modal analysis |

### Security Design

- Plugin sandbox (WASM or container isolation)
- Federation uses end-to-end encryption (no server access)
- Fine-tuning data never leaves local infrastructure
- Legacy mode with dead-man-switch and trustee access
- Marketplace code review before publication
- Supply chain security for plugins

### Deployment Strategy

- Hybrid: local core + optional cloud acceleration
- Edge deployment for low-latency voice
- CDN for marketplace assets
- Multi-region for federation relay (optional)

### Cost Estimates (Monthly)

| Item | Cost |
|------|------|
| AI APIs | $500–1,500 |
| Infrastructure (full stack) | $100–300 |
| Fine-tuning compute (episodic) | $50–200 |
| Data feeds | $200–500 |
| Federation relay (optional) | $30–60 |
| **Total** | **$880–2,560/mo** |

### Risks

| Risk | Mitigation |
|------|-----------|
| Plugin security | WASM sandbox; code review |
| Federation privacy leak | E2E encryption; no server decryption |
| Fine-tuning quality | Evaluation benchmarks; rollback |
| Ecosystem fragmentation | Strong SDK; quality marketplace curation |
| Long-term maintenance | Modular architecture; comprehensive docs |

### Testing Strategy

- Plugin sandbox escape testing
- Federation encryption verification
- Fine-tuning quality benchmarks
- Multi-modal accuracy evaluation
- Legacy mode simulation
- 10-year data migration test (schema evolution)
- Full platform regression suite

---

## Timeline Summary

```
Phase 1 (MVP)           ████████░░░░░░░░░░░░  Months 1–3
Phase 2 (Beta)          ░░░░░░░░████████░░░░  Months 4–6
Phase 3 (Production)    ░░░░░░░░░░░░░░████████████  Months 7–12
Phase 4 (Automation)    ░░░░░░░░░░░░░░░░░░░░░░████████  Months 13–18
Phase 5 (Ecosystem)     ░░░░░░░░░░░░░░░░░░░░░░░░░░████████████  Months 19–36
```

## Success Metrics

| Metric | Phase 1 | Phase 3 | Phase 5 |
|--------|---------|---------|---------|
| Memory entries | 100+ | 10,000+ | 100,000+ |
| Daily interactions | 5+ | 20+ | 50+ |
| Research reports | 10+ | 500+ | 5,000+ |
| Agent accuracy (user rating) | 70% | 85% | 95% |
| Uptime | 95% | 99% | 99.9% |
| Response latency (p95) | <5s | <3s | <2s |

## Current Status

**Phase 1 MVP — Foundation Complete**

The repository contains a working foundation:
- Backend with all 11 layer stubs and core implementations
- Command center frontend
- Docker infrastructure
- Database schema and migrations
- 9 agents, research engine, luxury module
- Architecture and roadmap documentation

**Next steps:** Configure API keys in `.env`, run `scripts/dev-setup.sh`, and begin daily use to accumulate memory.
