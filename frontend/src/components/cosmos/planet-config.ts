/** Nine agent-planets — shared 2D/3D config */

export type PlanetKind = "ringed" | "data" | "cloud" | "luxe" | "ocean" | "glyph" | "ink" | "facet" | "grid";

export interface CosmosPlanet {
  label: string;
  agentType: string;
  kind: PlanetKind;
  /** Base orbit angle in radians */
  angle: number;
  /** Orbit radius in world units */
  radius: number;
  /** Orbital speed multiplier */
  speed: number;
  /** Orbital plane tilt */
  inclination: number;
  /** Planet mesh scale */
  size: number;
}

export const COSMOS_PLANETS: CosmosPlanet[] = [
  { label: "EA", agentType: "executive_assistant", kind: "ringed", angle: 0, radius: 5.2, speed: 0.22, inclination: 0.15, size: 0.55 },
  { label: "RA", agentType: "research_analyst", kind: "data", angle: 0.72, radius: 6.1, speed: 0.18, inclination: -0.22, size: 0.48 },
  { label: "CG", agentType: "concierge", kind: "cloud", angle: 1.45, radius: 5.6, speed: 0.25, inclination: 0.35, size: 0.52 },
  { label: "LX", agentType: "luxury_analyst", kind: "luxe", angle: 2.1, radius: 7.0, speed: 0.16, inclination: -0.12, size: 0.5 },
  { label: "TR", agentType: "travel", kind: "ocean", angle: 2.85, radius: 6.4, speed: 0.2, inclination: 0.28, size: 0.54 },
  { label: "KL", agentType: "knowledge_librarian", kind: "glyph", angle: 3.55, radius: 5.8, speed: 0.24, inclination: -0.3, size: 0.46 },
  { label: "WR", agentType: "writing", kind: "ink", angle: 4.25, radius: 6.8, speed: 0.17, inclination: 0.18, size: 0.5 },
  { label: "PR", agentType: "presentation", kind: "facet", angle: 5.0, radius: 5.4, speed: 0.26, inclination: -0.25, size: 0.47 },
  { label: "OP", agentType: "operations", kind: "grid", angle: 5.75, radius: 7.2, speed: 0.15, inclination: 0.1, size: 0.53 },
];

export function planetByAgent(agentType?: string): CosmosPlanet | undefined {
  if (!agentType) return undefined;
  return COSMOS_PLANETS.find((p) => p.agentType === agentType);
}

export function planetByLabel(label?: string): CosmosPlanet | undefined {
  if (!label) return undefined;
  return COSMOS_PLANETS.find((p) => p.label === label);
}

/** HSL string → THREE hex-ish color helper inputs */
export function hslToColor(hsl: string): string {
  return `hsl(${hsl})`;
}
