import { grahaByAgent, type GrahaId, type Navagraha, NAVAGRAHA } from "./navagraha-config";

export interface GrahaRoutingCandidate {
  graha: Navagraha;
  score: number;
  reason: string;
}

export interface NavagrahaRouting {
  lead: Navagraha;
  supporting: Navagraha[];
  candidates: GrahaRoutingCandidate[];
}

/** Mirror backend heuristic scoring — instant client-side analysis */
export function analyzeNavagrahaRouting(query: string): NavagrahaRouting {
  const q = query.toLowerCase();
  const rules: { agentType: string; keywords: string[]; base: number }[] = [
    { agentType: "research_analyst", keywords: ["research", "analyze", "study", "report", "cite"], base: 90 },
    { agentType: "travel", keywords: ["travel", "trip", "itinerary", "flight", "hotel", "visa", "visit"], base: 92 },
    { agentType: "luxury_analyst", keywords: ["luxury", "uhni", "watch", "yacht", "auction", "collectible"], base: 88 },
    { agentType: "concierge", keywords: ["concierge", "reservation", "restaurant", "experience", "dining"], base: 86 },
    { agentType: "knowledge_librarian", keywords: ["remember", "memory", "knowledge", "recall", "library"], base: 84 },
    { agentType: "writing", keywords: ["write", "email", "letter", "draft", "compose"], base: 87 },
    { agentType: "presentation", keywords: ["presentation", "slide", "deck", "pitch"], base: 89 },
    { agentType: "operations", keywords: ["vendor", "household", "maintenance", "operations", "logistics"], base: 83 },
    { agentType: "executive_assistant", keywords: ["briefing", "priority", "calendar", "schedule", "day"], base: 85 },
  ];

  const scored: GrahaRoutingCandidate[] = NAVAGRAHA.map((graha) => {
    const rule = rules.find((r) => r.agentType === graha.agentType);
    const keywords = rule?.keywords ?? [];
    const base = rule?.base ?? 20;
    const hits = keywords.filter((kw) => q.includes(kw)).length;
    const score = hits ? Math.min(98, base + hits * 3) : 20;
    return {
      graha,
      score,
      reason: hits ? `Keyword match (${hits} signals)` : "General capability",
    };
  });

  if (!scored.some((c) => c.score > 50)) {
    const surya = grahaByAgent("executive_assistant")!;
    const idx = scored.findIndex((c) => c.graha.id === "surya");
    if (idx >= 0) {
      scored[idx] = { graha: surya, score: 75, reason: "Default Rudra routing" };
    }
  }

  scored.sort((a, b) => b.score - a.score);
  const lead = scored[0].graha;
  const supporting = scored
    .slice(1, 4)
    .filter((c) => c.score >= 40)
    .map((c) => c.graha);

  return { lead, supporting, candidates: scored };
}

export function grahaIdFromAgent(agentType?: string): GrahaId | undefined {
  return grahaByAgent(agentType)?.id;
}

/** Major queries trigger full damru roll */
export function isMajorQuery(query: string): boolean {
  if (query.length > 120) return true;
  return /research|strateg|plan|architect|analy[sz]|report|brief|design|build|code|develop|implement/i.test(
    query
  );
}
