---
name: daily-briefing
description: Produce the owner's concise morning briefing from recent memory and priorities.
---

# Daily Briefing

Produce an executive-grade morning briefing:

1. Use `search_memory` (queries like "priorities", "follow-ups", "commitments") to recall recent context.
2. Use `current_time` to anchor the briefing to today.
3. Output three short sections:
   - **Top Priorities** (max 5, ranked)
   - **Follow-ups** (open loops to close)
   - **Heads-up** (anything time-sensitive)
4. Be concise and actionable — no filler, no preamble.
