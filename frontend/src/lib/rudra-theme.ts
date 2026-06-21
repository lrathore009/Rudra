/** Trishula Cosmos theme — Navagraha tokens, facet colors, copy helpers */

export type RudraThemeMode = "sandhya" | "nisha" | "auto";
export type CoreRhythm = "idle" | "enriching" | "streaming" | "error";

/** Navagraha display names keyed by internal agent type */
export const GRAHA_BY_AGENT: Record<string, string> = {
  executive_assistant: "Surya",
  research_analyst: "Guru",
  concierge: "Rahu",
  luxury_analyst: "Shukra",
  travel: "Mangal",
  knowledge_librarian: "Ketu",
  writing: "Chandra",
  presentation: "Budha",
  operations: "Shani",
};

/** @deprecated Use grahaName() — kept for legacy tablet components */
export const AGENT_TAG: Record<string, string> = Object.fromEntries(
  Object.entries(GRAHA_BY_AGENT).map(([k, v]) => [k, v.slice(0, 3).toUpperCase()])
);

/** Navagraha accent hues */
export const GRAHA_COLOR: Record<string, string> = {
  Surya: "45 90% 58%",
  Chandra: "210 18% 78%",
  Mangal: "8 75% 48%",
  Budha: "155 55% 48%",
  Guru: "38 80% 55%",
  Shukra: "330 45% 68%",
  Shani: "220 25% 35%",
  Rahu: "280 55% 42%",
  Ketu: "265 60% 58%",
};

/** @deprecated Use GRAHA_COLOR */
export const FACET_COLOR: Record<string, string> = {
  ...GRAHA_COLOR,
  EA: GRAHA_COLOR.Surya,
  RA: GRAHA_COLOR.Guru,
  CG: GRAHA_COLOR.Rahu,
  LX: GRAHA_COLOR.Shukra,
  TR: GRAHA_COLOR.Mangal,
  KL: GRAHA_COLOR.Ketu,
  WR: GRAHA_COLOR.Chandra,
  PR: GRAHA_COLOR.Budha,
  OP: GRAHA_COLOR.Shani,
};

export const SUTRA_TICKER = [
  "Memory lattice synced",
  "Rudra commands the Navagraha",
  "Nine Grahas · one Trishula",
  "Local · sealed · yours",
  "The cosmos remembers",
];

export const FOOTER_TICKER_SEGMENTS = [
  "Memory lattice synced",
  "Signal before answer",
  "Encrypted counsel channel",
  "Navagraha routing live",
];

export const RUDRA_TAGLINE = "The void holds your counsel";

export function grahaName(agentType?: string): string | undefined {
  if (!agentType) return undefined;
  return GRAHA_BY_AGENT[agentType];
}

/** @deprecated Use grahaName() */
export function agentTag(agentType?: string): string | undefined {
  return grahaName(agentType);
}

export function grahaColor(name?: string, alpha = 1): string {
  if (!name || !GRAHA_COLOR[name]) return `hsl(var(--cosmos-cyan) / ${alpha})`;
  return `hsl(${GRAHA_COLOR[name]} / ${alpha})`;
}

export function facetHue(tag?: string): string {
  if (!tag) return "hsl(var(--cosmos-cyan))";
  const c = GRAHA_COLOR[tag] ?? FACET_COLOR[tag];
  return c ? `hsl(${c})` : "hsl(var(--cosmos-cyan))";
}

export function facetColor(tag?: string, alpha = 1): string {
  if (!tag) return `hsl(var(--cosmos-cyan) / ${alpha})`;
  const c = GRAHA_COLOR[tag] ?? FACET_COLOR[tag];
  return c ? `hsl(${c} / ${alpha})` : `hsl(var(--cosmos-cyan) / ${alpha})`;
}

export function resolveThemeMode(mode: RudraThemeMode, hour: number): "sandhya" | "nisha" {
  if (mode === "sandhya") return "sandhya";
  if (mode === "nisha") return "nisha";
  return hour >= 6 && hour < 18 ? "sandhya" : "nisha";
}

export function themeModeLabel(mode: RudraThemeMode): string {
  if (mode === "auto") return "AUTO";
  if (mode === "sandhya") return "NEBULA";
  return "VOID";
}

export function sutraPlaceholder(hour: number, processing: boolean): string {
  if (processing) return "Third eye opening…";
  return "What wisdom do you seek — or speak now";
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
  if (hour >= 5 && hour < 12) return "The Navagraha await Rudra's command";
  if (hour >= 12 && hour < 17) return "Nine Grahas orbit the Trishula";
  if (hour >= 17 && hour < 21) return "Nebula phase — command before rest";
  return "The void holds your counsel";
}

export const FIRST_BREATH_KEY = "rudra-first-breath";
