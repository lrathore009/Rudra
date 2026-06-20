/** Trishula Cosmos theme — shared tokens, facet colors, copy helpers */

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

/** Planet facet accent hues — internal UI only, never in chat voice */
export const FACET_COLOR: Record<string, string> = {
  EA: "190 95% 62%",
  RA: "210 55% 58%",
  CG: "165 45% 50%",
  LX: "328 55% 58%",
  TR: "200 60% 55%",
  KL: "85 40% 48%",
  WR: "25 60% 55%",
  PR: "270 45% 62%",
  OP: "145 45% 46%",
};

export const SUTRA_TICKER = [
  "Nine planets, one trident",
  "Local · sealed · yours",
  "The cosmos remembers",
  "Signal before answer",
  "Encrypted uplink · active",
];

export function agentTag(agentType?: string): string | undefined {
  if (!agentType) return undefined;
  return AGENT_TAG[agentType];
}

export function facetHue(tag?: string): string {
  if (!tag) return "hsl(var(--cosmos-cyan))";
  const c = FACET_COLOR[tag];
  return c ? `hsl(${c})` : "hsl(var(--cosmos-cyan))";
}

export function facetColor(tag?: string, alpha = 1): string {
  if (!tag || !FACET_COLOR[tag]) return `hsl(var(--cosmos-cyan) / ${alpha})`;
  return `hsl(${FACET_COLOR[tag]} / ${alpha})`;
}

export function resolveThemeMode(mode: RudraThemeMode, hour: number): "sandhya" | "nisha" {
  if (mode === "sandhya") return "sandhya";
  if (mode === "nisha") return "nisha";
  return hour >= 6 && hour < 18 ? "sandhya" : "nisha";
}

/** Display label for theme cycle (internal keys stay sandhya/nisha for localStorage) */
export function themeModeLabel(mode: RudraThemeMode): string {
  if (mode === "auto") return "AUTO";
  if (mode === "sandhya") return "NEBULA";
  return "VOID";
}

export function sutraPlaceholder(hour: number, processing: boolean): string {
  if (processing) return "third eye opening…";
  if (hour >= 5 && hour < 12) return "What shall we illuminate today?";
  if (hour >= 12 && hour < 17) return "Transmit your command…";
  if (hour >= 17 && hour < 21) return "What remains before rest?";
  return "Close the orbit — what remains?";
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
  if (hour >= 5 && hour < 12) return "The dawn sector awaits your signal";
  if (hour >= 12 && hour < 17) return "All nine planets are listening";
  if (hour >= 17 && hour < 21) return "Nebula phase — command before rest";
  return "The void holds your counsel";
}

export const FIRST_BREATH_KEY = "rudra-first-breath";
