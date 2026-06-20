# Knowledge Graph

Rudra links memories, projects, and documents through a personal knowledge graph.

## Data model

| Table | Purpose |
|-------|---------|
| `entities` | People, companies, projects, apps, topics, etc. |
| `entity_aliases` | Alternate names |
| `graph_relationships` | `owns`, `works_on`, `related_to`, … |
| `memory_entity_links` | Memory ↔ entity mentions |
| `project_entity_links` | Project ↔ entity links |

## APIs

- `GET /api/v1/graph/entities`
- `GET /api/v1/graph/entities/{id}`
- `GET /api/v1/graph/entities/{id}/memories`
- `GET /api/v1/graph/relationships`
- `POST /api/v1/graph/relationships`
- `POST /api/v1/graph/extract`

## Extraction

Rule-based matching against seeded Vikram/Rudra ecosystem entities plus proper-noun detection. Optional LLM extraction via `use_llm=true`.

Memories auto-link entities on create.

## HUD

**Knowledge Graph** panel (right column): searchable entity list, detail drawer, relationships, linked memories.

## Seed data

Bootstrapped on startup: Vikram Rathore, Rudra OS, Jobsflix portfolio, Sphere projects, etc.
