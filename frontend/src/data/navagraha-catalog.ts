/**
 * Navagraha catalog — authoritative 2D panel copy + 3D visual params.
 *
 * Jyotish karaka (significations): Brihat Parashara Hora Shastra, classical
 * graha portfolios; cross-checked with jyotishvidya.com / VedicBirth summaries.
 * Physical mapping: NASA Solar System Exploration / JPL fact sheets for textures
 * and relative scale; Rahu/Ketu are lunar nodes (no physical body).
 */

import { grahaPosition3D } from "@/components/cosmos/orbit-math";
import type { GrahaId, GrahaSurface, Navagraha } from "@/components/cosmos/navagraha-types";

export type { GrahaId } from "@/components/cosmos/navagraha-types";

const T = "/textures/planets";

/** Classical karaka keywords shown on Prime graha panels */
export interface GrahaPanelSpec {
  id: GrahaId;
  /** Sanskrit name (Roman) */
  name: string;
  symbol: string;
  /** Primary Jyotish significations — concise, not invented */
  attributes: string[];
  position: { leftPct: number; topPct: number };
  align: "left" | "right";
  glow: string;
  agentType: string;
}

export const SANCTUM_DEFAULT_COUNSEL =
  "Be still. Command not the answer, but the silence before it. Nine grahas orbit; the Trishula holds the still point. Ask, and counsel will arise from the void.";

/** Panel layout tuned to rudra-prime-reference.png */
export const GRAHA_PANELS: GrahaPanelSpec[] = [
  {
    id: "surya",
    name: "Surya",
    symbol: "☉",
    attributes: ["Atma", "Soul", "Father", "Authority", "Vitality"],
    position: { leftPct: 14, topPct: 22 },
    align: "left",
    glow: "#e8a030",
    agentType: "executive_assistant",
  },
  {
    id: "mangal",
    name: "Mangal",
    symbol: "♂",
    attributes: ["Courage", "Energy", "Action", "Brothers", "Land"],
    position: { leftPct: 12, topPct: 38 },
    align: "left",
    glow: "#c04030",
    agentType: "travel",
  },
  {
    id: "budha",
    name: "Budha",
    symbol: "☿",
    attributes: ["Buddhi", "Intellect", "Speech", "Commerce", "Skills"],
    position: { leftPct: 11, topPct: 52 },
    align: "left",
    glow: "#48a878",
    agentType: "presentation",
  },
  {
    id: "guru",
    name: "Guru",
    symbol: "♃",
    attributes: ["Guru", "Wisdom", "Dharma", "Children", "Fortune"],
    position: { leftPct: 13, topPct: 66 },
    align: "left",
    glow: "#d4a840",
    agentType: "research_analyst",
  },
  {
    id: "shukra",
    name: "Shukra",
    symbol: "♀",
    attributes: ["Kama", "Love", "Arts", "Luxury", "Harmony"],
    position: { leftPct: 86, topPct: 22 },
    align: "right",
    glow: "#c890a8",
    agentType: "luxury_analyst",
  },
  {
    id: "chandra",
    name: "Chandra",
    symbol: "☽",
    attributes: ["Manas", "Mind", "Mother", "Emotions", "Nourishment"],
    position: { leftPct: 88, topPct: 36 },
    align: "right",
    glow: "#a8b8c8",
    agentType: "writing",
  },
  {
    id: "shani",
    name: "Shani",
    symbol: "♄",
    attributes: ["Karma", "Discipline", "Delay", "Justice", "Longevity"],
    position: { leftPct: 87, topPct: 50 },
    align: "right",
    glow: "#607890",
    agentType: "operations",
  },
  {
    id: "rahu",
    name: "Rahu",
    symbol: "☊",
    attributes: ["Obsession", "Maya", "Foreign", "Innovation", "Desire"],
    position: { leftPct: 86, topPct: 64 },
    align: "right",
    glow: "#8868b0",
    agentType: "concierge",
  },
  {
    id: "ketu",
    name: "Ketu",
    symbol: "☋",
    attributes: ["Moksha", "Detachment", "Past Karma", "Insight", "Liberation"],
    position: { leftPct: 84, topPct: 78 },
    align: "right",
    glow: "#808890",
    agentType: "knowledge_librarian",
  },
];

/** Orbital inclination (deg) — stylized geocentric Navagraha mandala, not J2000 ephemeris */
const ORBIT_INCLINATION: Record<GrahaId, number> = {
  surya: 14,
  chandra: 22,
  mangal: 32,
  budha: -12,
  guru: -18,
  shukra: 28,
  shani: -30,
  rahu: 38,
  ketu: 42,
};

/** NASA/JPL-inspired relative radii (Earth = 1), scaled for scene legibility */
const RELATIVE_RADIUS: Record<GrahaId, number> = {
  surya: 109,
  guru: 11.2,
  shani: 9.45,
  shukra: 0.95,
  mangal: 0.53,
  budha: 0.38,
  chandra: 0.27,
  rahu: 0.35,
  ketu: 0.32,
};

function sceneRadius(id: GrahaId): number {
  const r = RELATIVE_RADIUS[id];
  const base = 0.14 + (r / 109) * 0.52;
  return Math.min(0.62, Math.max(0.18, base));
}

type SceneSeed = Omit<Navagraha, "orbitInclination" | "orbitAscending" | "rimAngle">;

const SCENE_SEED: SceneSeed[] = [
  {
    id: "surya",
    name: "Surya",
    tag: "SUR",
    symbol: "☉",
    domain: "Atma · Leadership",
    agentType: "executive_assistant",
    orbitRadiusX: 11.5,
    orbitRadiusZ: 4.0,
    orbitLift: 2.5,
    orbitColor: "#ffaa33",
    screenLabel: { leftPct: 14, topPct: 22 },
    labelOffsetX: 0.45,
    labelOffsetY: 0.9,
    speed: 0.06,
    angle: 0.55,
    size: sceneRadius("surya"),
    axialTilt: 7.25,
    surface: "corona",
    texture: `${T}/2k_sun.jpg`,
    appearance: {
      color: "#ffb840",
      emissive: "#ff8800",
      emissiveIntensity: 1.2,
      metalness: 0.15,
      roughness: 0.35,
    },
  },
  {
    id: "chandra",
    name: "Chandra",
    tag: "CHN",
    symbol: "☽",
    domain: "Manas · Mind",
    agentType: "writing",
    orbitRadiusX: 10.0,
    orbitRadiusZ: 3.8,
    orbitLift: 2.2,
    orbitColor: "#aaccee",
    screenLabel: { leftPct: 88, topPct: 36 },
    labelOffsetX: -0.5,
    labelOffsetY: 0.85,
    speed: 0.07,
    angle: 2.85,
    size: sceneRadius("chandra"),
    axialTilt: 6.68,
    surface: "default",
    texture: `${T}/2k_moon.jpg`,
    appearance: {
      color: "#d8e4f0",
      emissive: "#667788",
      emissiveIntensity: 0.15,
      metalness: 0.05,
      roughness: 0.92,
    },
  },
  {
    id: "mangal",
    name: "Mangal",
    tag: "MAN",
    symbol: "♂",
    domain: "Energy · Action",
    agentType: "travel",
    orbitRadiusX: 10.6,
    orbitRadiusZ: 3.8,
    orbitLift: 0.3,
    orbitColor: "#ee4422",
    screenLabel: { leftPct: 12, topPct: 38 },
    labelOffsetX: -0.55,
    labelOffsetY: 0.7,
    speed: 0.07,
    angle: 3.15,
    size: sceneRadius("mangal"),
    axialTilt: 25.19,
    surface: "default",
    texture: `${T}/2k_mars.jpg`,
    appearance: { color: "#c1440e", emissive: "#000000", emissiveIntensity: 0, metalness: 0.1, roughness: 0.88 },
  },
  {
    id: "budha",
    name: "Budha",
    tag: "BUD",
    symbol: "☿",
    domain: "Intellect · Speech",
    agentType: "presentation",
    orbitRadiusX: 10.2,
    orbitRadiusZ: 3.6,
    orbitLift: -1.0,
    orbitColor: "#44dd99",
    screenLabel: { leftPct: 11, topPct: 52 },
    labelOffsetX: -0.55,
    labelOffsetY: -0.8,
    speed: 0.075,
    angle: 3.65,
    size: sceneRadius("budha"),
    axialTilt: 0.034,
    surface: "default",
    texture: `${T}/2k_mercury.jpg`,
    appearance: { color: "#8c8b8a", emissive: "#000000", emissiveIntensity: 0, metalness: 0.35, roughness: 0.75 },
  },
  {
    id: "guru",
    name: "Guru",
    tag: "GUR",
    symbol: "♃",
    domain: "Wisdom · Dharma",
    agentType: "research_analyst",
    orbitRadiusX: 12.0,
    orbitRadiusZ: 4.3,
    orbitLift: -1.5,
    orbitColor: "#ddaa44",
    screenLabel: { leftPct: 13, topPct: 66 },
    labelOffsetX: 0.5,
    labelOffsetY: -0.85,
    speed: 0.05,
    angle: 5.55,
    size: sceneRadius("guru"),
    axialTilt: 3.13,
    surface: "banded",
    texture: `${T}/2k_jupiter.jpg`,
    appearance: { color: "#c88b3a", emissive: "#000000", emissiveIntensity: 0, metalness: 0.05, roughness: 0.82 },
  },
  {
    id: "shukra",
    name: "Shukra",
    tag: "SHK",
    symbol: "♀",
    domain: "Kama · Harmony",
    agentType: "luxury_analyst",
    orbitRadiusX: 11.2,
    orbitRadiusZ: 4.1,
    orbitLift: 2.6,
    orbitColor: "#ff77aa",
    screenLabel: { leftPct: 86, topPct: 22 },
    labelOffsetX: 0.5,
    labelOffsetY: 0.85,
    speed: 0.065,
    angle: 1.05,
    size: sceneRadius("shukra"),
    axialTilt: 177.36,
    surface: "default",
    texture: `${T}/2k_venus_surface.jpg`,
    appearance: { color: "#e6c89c", emissive: "#000000", emissiveIntensity: 0, metalness: 0.08, roughness: 0.65 },
  },
  {
    id: "shani",
    name: "Shani",
    tag: "SHA",
    symbol: "♄",
    domain: "Karma · Discipline",
    agentType: "operations",
    orbitRadiusX: 10.8,
    orbitRadiusZ: 3.7,
    orbitLift: -2.2,
    orbitColor: "#7799bb",
    screenLabel: { leftPct: 87, topPct: 50 },
    labelOffsetX: 0,
    labelOffsetY: -0.95,
    speed: 0.05,
    angle: 4.75,
    size: sceneRadius("shani"),
    axialTilt: 26.73,
    surface: "default",
    texture: `${T}/2k_saturn.jpg`,
    hasRings: true,
    appearance: { color: "#c9b896", emissive: "#000000", emissiveIntensity: 0, metalness: 0.12, roughness: 0.78 },
  },
  {
    id: "rahu",
    name: "Rahu",
    tag: "RAH",
    symbol: "☊",
    domain: "North Node · Maya",
    agentType: "concierge",
    orbitRadiusX: 11.0,
    orbitRadiusZ: 4.2,
    orbitLift: 2.8,
    orbitColor: "#bb55ff",
    screenLabel: { leftPct: 86, topPct: 64 },
    labelOffsetX: -0.4,
    labelOffsetY: 0.9,
    speed: 0.06,
    angle: 2.35,
    size: sceneRadius("rahu"),
    axialTilt: 0,
    surface: "swirl",
    appearance: {
      color: "#5522aa",
      emissive: "#9933ff",
      emissiveIntensity: 0.65,
      metalness: 0.4,
      roughness: 0.45,
    },
  },
  {
    id: "ketu",
    name: "Ketu",
    tag: "KET",
    symbol: "☋",
    domain: "South Node · Moksha",
    agentType: "knowledge_librarian",
    orbitRadiusX: 10.5,
    orbitRadiusZ: 3.9,
    orbitLift: 0.5,
    orbitColor: "#9999aa",
    screenLabel: { leftPct: 84, topPct: 78 },
    labelOffsetX: 0.55,
    labelOffsetY: 0.75,
    speed: 0.07,
    angle: 0.15,
    size: sceneRadius("ketu"),
    axialTilt: 0,
    surface: "hex",
    appearance: {
      color: "#666677",
      emissive: "#8899aa",
      emissiveIntensity: 0.35,
      metalness: 0.55,
      roughness: 0.5,
    },
  },
];

/** Full Navagraha records for 3D scene (incl. orbit math fields) */
export const SANCTUM_GRAHAS: Navagraha[] = SCENE_SEED.map((g) => ({
  ...g,
  orbitInclination: ORBIT_INCLINATION[g.id],
  orbitAscending: (g.angle * 180) / Math.PI,
  rimAngle: g.angle,
}));

export const SANCTUM_STARS = `${T}/2k_stars_milky_way.jpg`;
export const SANCTUM_TRISHUL_SCALE = 3.25;
export const SANCTUM_EYE_OFFSET = { x: 0, y: 0.15, z: 0.16 } as const;

export function catalogGrahaById(id?: GrahaId): (Navagraha & GrahaPanelSpec) | undefined {
  if (!id) return undefined;
  const scene = SANCTUM_GRAHAS.find((g) => g.id === id);
  const panel = GRAHA_PANELS.find((g) => g.id === id);
  if (!scene || !panel) return undefined;
  return { ...scene, ...panel };
}

export function catalogGrahaByAgent(agentType?: string): Navagraha | undefined {
  if (!agentType) return undefined;
  return SANCTUM_GRAHAS.find((g) => g.agentType === agentType);
}

export function sanctumGrahaPosition(graha: Navagraha, theta: number) {
  const v = grahaPosition3D(graha, theta);
  return { x: v.x, y: v.y, z: v.z };
}

export function panelForGraha(id: GrahaId): GrahaPanelSpec | undefined {
  return GRAHA_PANELS.find((g) => g.id === id);
}

export function grahaSurfaceKind(id: GrahaId): GrahaSurface {
  return SANCTUM_GRAHAS.find((g) => g.id === id)?.surface ?? "default";
}
