/** Nine agent-planets mapped to real solar system bodies (Solar System Scope textures) */

import type { SolarBody } from "./solar-textures";
import { ORBIT_RADII, planetWorldSize } from "./cosmos-scale";

export interface CosmosPlanet {
  label: string;
  agentType: string;
  solarBody: SolarBody;
  solarName: string;
  angle: number;
  radius: number;
  speed: number;
  inclination: number;
  size: number;
  spin: number;
}

/** Agent ↔ solar body alignment — orbits and sizes relative to Trishul scale */
export const COSMOS_PLANETS: CosmosPlanet[] = [
  {
    label: "EA",
    agentType: "executive_assistant",
    solarBody: "earth",
    solarName: "Earth",
    angle: 0,
    radius: ORBIT_RADII.earth,
    speed: 0.28,
    inclination: 0.08,
    size: planetWorldSize("earth"),
    spin: 0.35,
  },
  {
    label: "RA",
    agentType: "research_analyst",
    solarBody: "jupiter",
    solarName: "Jupiter",
    angle: 0.9,
    radius: ORBIT_RADII.jupiter,
    speed: 0.12,
    inclination: -0.06,
    size: planetWorldSize("jupiter"),
    spin: 0.55,
  },
  {
    label: "CG",
    agentType: "concierge",
    solarBody: "venus",
    solarName: "Venus",
    angle: 1.8,
    radius: ORBIT_RADII.venus,
    speed: 0.32,
    inclination: 0.04,
    size: planetWorldSize("venus"),
    spin: -0.08,
  },
  {
    label: "LX",
    agentType: "luxury_analyst",
    solarBody: "saturn",
    solarName: "Saturn",
    angle: 2.6,
    radius: ORBIT_RADII.saturn,
    speed: 0.1,
    inclination: 0.12,
    size: planetWorldSize("saturn"),
    spin: 0.48,
  },
  {
    label: "TR",
    agentType: "travel",
    solarBody: "neptune",
    solarName: "Neptune",
    angle: 3.5,
    radius: ORBIT_RADII.neptune,
    speed: 0.08,
    inclination: -0.1,
    size: planetWorldSize("neptune"),
    spin: 0.42,
  },
  {
    label: "KL",
    agentType: "knowledge_librarian",
    solarBody: "mercury",
    solarName: "Mercury",
    angle: 4.2,
    radius: ORBIT_RADII.mercury,
    speed: 0.38,
    inclination: 0.14,
    size: planetWorldSize("mercury"),
    spin: 0.12,
  },
  {
    label: "WR",
    agentType: "writing",
    solarBody: "mars",
    solarName: "Mars",
    angle: 5.0,
    radius: ORBIT_RADII.mars,
    speed: 0.22,
    inclination: -0.08,
    size: planetWorldSize("mars"),
    spin: 0.38,
  },
  {
    label: "PR",
    agentType: "presentation",
    solarBody: "uranus",
    solarName: "Uranus",
    angle: 5.8,
    radius: ORBIT_RADII.uranus,
    speed: 0.09,
    inclination: 0.78,
    size: planetWorldSize("uranus"),
    spin: -0.35,
  },
  {
    label: "OP",
    agentType: "operations",
    solarBody: "moon",
    solarName: "Moon",
    angle: 0.35,
    radius: ORBIT_RADII.moon,
    speed: 0.45,
    inclination: 0.18,
    size: planetWorldSize("moon"),
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
