/** Rudraksha theme — shared tokens, facet colors, copy helpers */

export type RudraThemeMode = "sandhya" | "nisha" | "auto";
export type CoreRhythm = "idle" | "enriching" | "streaming" | "error";

export const AGENT_TAG: Record<string, string> = {
  executive_assistant: "EA",
  research_analyst: "RA",
  concierge: "CG",
  luxury_analyst: "LX",
  travel: "TR",
  knowledge_librarian: "KL",
  writing: "WR",
  presentation: "PR",
  operations: "OP",
};

/** Muted facet accent hues — internal UI only, never in chat voice */
export const FACET_COLOR: Record<string, string> = {
  EA: "38 92% 58%",
  RA: "210 45% 52%",
  CG: "165 40% 45%",
  LX: "340 35% 48%",
  TR: "200 50% 50%",
  KL: "85 35% 42%",
  WR: "25 55% 50%",
  PR: "270 30% 55%",
  OP: "145 40% 40%",
};

export const SUTRA_TICKER = [
  "Nine facets, one voice",
  "Local · sealed · yours",
  "The mala remembers",
  "Contemplation before answer",
  "Sacred link · encrypted",
];

export function agentTag(agentType?: string): string | undefined {
  if (!agentType) return undefined;
  return AGENT_TAG[agentType];
}

export function facetHue(tag?: string): string {
  if (!tag) return "hsl(var(--rudra-gold))";
  const c = FACET_COLOR[tag];
  return c ? `hsl(${c})` : "hsl(var(--rudra-gold))";
}

export function facetColor(tag?: string, alpha = 1): string {
  if (!tag || !FACET_COLOR[tag]) return `hsl(var(--rudra-gold) / ${alpha})`;
  return `hsl(${FACET_COLOR[tag]} / ${alpha})`;
}

export function resolveThemeMode(mode: RudraThemeMode, hour: number): "sandhya" | "nisha" {
  if (mode === "sandhya") return "sandhya";
  if (mode === "nisha") return "nisha";
  return hour >= 6 && hour < 18 ? "sandhya" : "nisha";
}

export function sutraPlaceholder(hour: number, processing: boolean): string {
  if (processing) return "contemplating…";
  if (hour >= 5 && hour < 12) return "What shall we illuminate today?";
  if (hour >= 12 && hour < 17) return "Offer your sutra…";
  if (hour >= 17 && hour < 21) return "What remains before rest?";
  return "Close the day — what remains?";
}

export function coreRhythmFromState(
  processing: boolean,
  streaming: boolean,
  hasError: boolean,
  enriching: boolean
): CoreRhythm {
  if (hasError) return "error";
  if (streaming) return "streaming";
  if (processing && enriching) return "enriching";
  if (processing) return "enriching";
  return "idle";
}

export function hapticTap(pattern: number | number[] = 8): void {
  if (typeof navigator !== "undefined" && navigator.vibrate) {
    navigator.vibrate(pattern);
  }
}

export function worldGreeting(hour: number): string {
  if (hour >= 5 && hour < 12) return "The day awaits your word";
  if (hour >= 12 && hour < 17) return "The dominions are listening";
  if (hour >= 17 && hour < 21) return "Sandhya — command before rest";
  return "The night holds your counsel";
}

export const FIRST_BREATH_KEY = "rudra-first-breath";
