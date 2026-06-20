/** Nine agent-planets mapped to real solar system bodies (Solar System Scope textures) */

import type { SolarBody } from "./solar-textures";

export interface CosmosPlanet {
  label: string;
  agentType: string;
  /** Real solar system body for HD texture */
  solarBody: SolarBody;
  solarName: string;
  /** Base orbit angle in radians */
  angle: number;
  /** Orbit radius — inner → outer, log-scaled for visibility */
  radius: number;
  /** Orbital speed (inner planets faster) */
  speed: number;
  /** Orbital plane tilt in radians */
  inclination: number;
  /** Visual scale relative to Earth = 0.52 */
  size: number;
  /** Self-rotation speed */
  spin: number;
}

/** Agent ↔ solar body alignment */
export const COSMOS_PLANETS: CosmosPlanet[] = [
  {
    label: "EA",
    agentType: "executive_assistant",
    solarBody: "earth",
    solarName: "Earth",
    angle: 0,
    radius: 5.8,
    speed: 0.28,
    inclination: 0.08,
    size: 0.52,
    spin: 0.35,
  },
  {
    label: "RA",
    agentType: "research_analyst",
    solarBody: "jupiter",
    solarName: "Jupiter",
    angle: 0.9,
    radius: 9.2,
    speed: 0.12,
    inclination: -0.06,
    size: 0.88,
    spin: 0.55,
  },
  {
    label: "CG",
    agentType: "concierge",
    solarBody: "venus",
    solarName: "Venus",
    angle: 1.8,
    radius: 5.2,
    speed: 0.32,
    inclination: 0.04,
    size: 0.5,
    spin: -0.08,
  },
  {
    label: "LX",
    agentType: "luxury_analyst",
    solarBody: "saturn",
    solarName: "Saturn",
    angle: 2.6,
    radius: 10.5,
    speed: 0.1,
    inclination: 0.12,
    size: 0.74,
    spin: 0.48,
  },
  {
    label: "TR",
    agentType: "travel",
    solarBody: "neptune",
    solarName: "Neptune",
    angle: 3.5,
    radius: 12.8,
    speed: 0.08,
    inclination: -0.1,
    size: 0.56,
    spin: 0.42,
  },
  {
    label: "KL",
    agentType: "knowledge_librarian",
    solarBody: "mercury",
    solarName: "Mercury",
    angle: 4.2,
    radius: 4.5,
    speed: 0.38,
    inclination: 0.14,
    size: 0.38,
    spin: 0.12,
  },
  {
    label: "WR",
    agentType: "writing",
    solarBody: "mars",
    solarName: "Mars",
    angle: 5.0,
    radius: 6.5,
    speed: 0.22,
    inclination: -0.08,
    size: 0.44,
    spin: 0.38,
  },
  {
    label: "PR",
    agentType: "presentation",
    solarBody: "uranus",
    solarName: "Uranus",
    angle: 5.8,
    radius: 11.5,
    speed: 0.09,
    inclination: 0.78,
    size: 0.58,
    spin: -0.35,
  },
  {
    label: "OP",
    agentType: "operations",
    solarBody: "moon",
    solarName: "Moon",
    angle: 0.35,
    radius: 6.2,
    speed: 0.45,
    inclination: 0.18,
    size: 0.28,
    spin: 0.05,
  },
];

export function planetByAgent(agentType?: string): CosmosPlanet | undefined {
  if (!agentType) return undefined;
  return COSMOS_PLANETS.find((p) => p.agentType === agentType);
}

export function planetByLabel(label?: string): CosmosPlanet | undefined {
  if (!label) return undefined;
  return COSMOS_PLANETS.find((p) => p.label === label);
}
