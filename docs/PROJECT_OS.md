# Project Operating System (Founder OS)

Rudra tracks your active ventures as first-class operational objects.

## Data model

`founder_projects` plus `project_tasks`, `project_milestones`, `project_updates`, `project_metrics`.

## APIs

- `GET/POST /api/v1/projects`
- `GET/PATCH /api/v1/projects/{id}`
- `GET/POST /api/v1/projects/{id}/tasks`
- `PATCH /api/v1/projects/{id}/tasks/{task_id}`
- `POST /api/v1/projects/{id}/updates`
- `GET /api/v1/projects/dashboard`

## Intelligence

- Progress from task completion ratio
- Stale project detection (14+ days without update)
- Blocked project surfacing
- Next-action recommendations
- Weekly founder briefing text in dashboard

## Agent integration

Commands mentioning a project name (e.g. “What should I do next in ChemSphere?”) inject `project_context` into the agent metadata.

## HUD

**Founder OS** panel (left column): project cards, progress bars, priority filter, “Ask Rudra about this project”.

## Seed portfolio

Rudra OS, Jobsflix products, HumanEdge, AppHive, Sphere ventures, Equation Universe, etc.
