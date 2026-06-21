/** Rudra Prime — Navagraha tokens, facet colors, copy helpers */

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

export const SUTRA_TICKER = [
  "Memory lattice synced",
  "Rudra Prime online",
  "Nine Grahas · one Trishul",
  "Local · sealed · yours",
  "Voice-armed counsel channel",
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

export function grahaColor(name?: string, alpha = 1): string {
  if (!name || !GRAHA_COLOR[name]) return `hsl(195 100% 50% / ${alpha})`;
  return `hsl(${GRAHA_COLOR[name]} / ${alpha})`;
}

export function facetHue(tag?: string): string {
  if (!tag) return "hsl(195 100% 50%)";
  const c = GRAHA_COLOR[tag];
  return c ? `hsl(${c})` : "hsl(195 100% 50%)";
}

export function facetColor(tag?: string, alpha = 1): string {
  if (!tag) return `hsl(195 100% 50% / ${alpha})`;
  const c = GRAHA_COLOR[tag];
  return c ? `hsl(${c} / ${alpha})` : `hsl(195 100% 50% / ${alpha})`;
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
  if (hour >= 12 && hour < 17) return "Nine Grahas orbit the Trishul";
  if (hour >= 17 && hour < 21) return "Prime phase — command before rest";
  return "The void holds your counsel";
}

export const FIRST_BREATH_KEY = "rudra-first-breath";
