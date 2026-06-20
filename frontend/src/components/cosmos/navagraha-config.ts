/** Navagraha — nine cognitive forces orbiting Rudra (internal agent routing unchanged) */

export type GrahaId =
  | "surya"
  | "chandra"
  | "mangal"
  | "budha"
  | "guru"
  | "shukra"
  | "shani"
  | "rahu"
  | "ketu";

export interface Navagraha {
  id: GrahaId;
  /** Display name */
  name: string;
  /** Short label for telemetry */
  tag: string;
  agentType: string;
  /** Elliptical orbit — wide horizontal from front camera */
  orbitRadiusX: number;
  orbitRadiusZ: number;
  orbitLift: number;
  speed: number;
  angle: number;
  /** Sphere radius multiplier (Guru largest) */
  size: number;
  axialTilt: number;
  hasRings?: boolean;
  /** Symbolic appearance — not photorealistic */
  appearance: {
    color: string;
    emissive: string;
    emissiveIntensity: number;
    metalness: number;
    roughness: number;
    clearcoat?: number;
  };
}

/** Agent ↔ Navagraha (internal routing keys unchanged) */
export const NAVAGRAHA: Navagraha[] = [
  {
    id: "surya",
    name: "Surya",
    tag: "SUR",
    agentType: "executive_assistant",
    orbitRadiusX: 7.2,
    orbitRadiusZ: 2.4,
    orbitLift: 0.35,
    speed: 0.18,
    angle: 0,
    size: 0.28,
    axialTilt: 0.1,
    appearance: {
      color: "#ffd066",
      emissive: "#ff9922",
      emissiveIntensity: 0.55,
      metalness: 0.35,
      roughness: 0.38,
    },
  },
  {
    id: "chandra",
    name: "Chandra",
    tag: "CHN",
    agentType: "writing",
    orbitRadiusX: 5.8,
    orbitRadiusZ: 2.0,
    orbitLift: 0.28,
    speed: 0.22,
    angle: 0.72,
    size: 0.24,
    axialTilt: 0.06,
    appearance: {
      color: "#e4ecf8",
      emissive: "#99bbdd",
      emissiveIntensity: 0.35,
      metalness: 0.55,
      roughness: 0.22,
      clearcoat: 0.6,
    },
  },
  {
    id: "mangal",
    name: "Mangal",
    tag: "MAN",
    agentType: "travel",
    orbitRadiusX: 8.4,
    orbitRadiusZ: 2.8,
    orbitLift: 0.4,
    speed: 0.16,
    angle: 1.42,
    size: 0.22,
    axialTilt: 0.25,
    appearance: {
      color: "#cc3311",
      emissive: "#881100",
      emissiveIntensity: 0.25,
      metalness: 0.72,
      roughness: 0.28,
    },
  },
  {
    id: "budha",
    name: "Budha",
    tag: "BUD",
    agentType: "presentation",
    orbitRadiusX: 6.4,
    orbitRadiusZ: 2.2,
    orbitLift: 0.22,
    speed: 0.26,
    angle: 2.12,
    size: 0.23,
    axialTilt: 0.04,
    appearance: {
      color: "#33cc88",
      emissive: "#118855",
      emissiveIntensity: 0.4,
      metalness: 0.4,
      roughness: 0.35,
    },
  },
  {
    id: "guru",
    name: "Guru",
    tag: "GUR",
    agentType: "research_analyst",
    orbitRadiusX: 9.6,
    orbitRadiusZ: 3.0,
    orbitLift: 0.45,
    speed: 0.12,
    angle: 2.82,
    size: 0.34,
    axialTilt: 0.08,
    appearance: {
      color: "#eebb55",
      emissive: "#cc8822",
      emissiveIntensity: 0.45,
      metalness: 0.3,
      roughness: 0.42,
    },
  },
  {
    id: "shukra",
    name: "Shukra",
    tag: "SHK",
    agentType: "luxury_analyst",
    orbitRadiusX: 7.8,
    orbitRadiusZ: 2.6,
    orbitLift: 0.32,
    speed: 0.15,
    angle: 3.52,
    size: 0.26,
    axialTilt: 0.78,
    appearance: {
      color: "#ffe8f4",
      emissive: "#dd88aa",
      emissiveIntensity: 0.3,
      metalness: 0.25,
      roughness: 0.18,
      clearcoat: 0.85,
    },
  },
  {
    id: "shani",
    name: "Shani",
    tag: "SHA",
    agentType: "operations",
    orbitRadiusX: 10.2,
    orbitRadiusZ: 3.2,
    orbitLift: 0.18,
    speed: 0.1,
    angle: 4.22,
    size: 0.25,
    axialTilt: 0.47,
    hasRings: true,
    appearance: {
      color: "#1a1a28",
      emissive: "#223344",
      emissiveIntensity: 0.15,
      metalness: 0.65,
      roughness: 0.55,
    },
  },
  {
    id: "rahu",
    name: "Rahu",
    tag: "RAH",
    agentType: "concierge",
    orbitRadiusX: 6.8,
    orbitRadiusZ: 2.5,
    orbitLift: 0.38,
    speed: 0.2,
    angle: 4.92,
    size: 0.24,
    axialTilt: 0.15,
    appearance: {
      color: "#220033",
      emissive: "#6622aa",
      emissiveIntensity: 0.35,
      metalness: 0.5,
      roughness: 0.6,
    },
  },
  {
    id: "ketu",
    name: "Ketu",
    tag: "KET",
    agentType: "knowledge_librarian",
    orbitRadiusX: 5.2,
    orbitRadiusZ: 1.8,
    orbitLift: 0.25,
    speed: 0.24,
    angle: 5.62,
    size: 0.22,
    axialTilt: 0.12,
    appearance: {
      color: "#6644cc",
      emissive: "#aa66ff",
      emissiveIntensity: 0.5,
      metalness: 0.35,
      roughness: 0.4,
    },
  },
];

/** Milky Way backdrop (Solar System Scope stars texture) */
export const SSS_TEXTURE_BASE = "/textures/planets";
export const SSS_STARS_MILKY_WAY = `${SSS_TEXTURE_BASE}/2k_stars_milky_way.jpg`;

/** Third eye world offset from trishul root group origin */
export const THIRD_EYE_OFFSET = { x: 0, y: 0.07, z: 0.16 } as const;

export function grahaByAgent(agentType?: string): Navagraha | undefined {
  if (!agentType) return undefined;
  return NAVAGRAHA.find((g) => g.agentType === agentType);
}

export function grahaById(id?: GrahaId): Navagraha | undefined {
  if (!id) return undefined;
  return NAVAGRAHA.find((g) => g.id === id);
}

export function grahaByTag(tag?: string): Navagraha | undefined {
  if (!tag) return undefined;
  return NAVAGRAHA.find((g) => g.tag === tag || g.name === tag);
}

export function grahaPosition(graha: Navagraha, angle: number): { x: number; y: number; z: number } {
  const x = Math.cos(angle) * graha.orbitRadiusX;
  const z = Math.sin(angle) * graha.orbitRadiusZ;
  const y = Math.sin(angle * 0.5 + graha.angle) * graha.orbitLift;
  return { x, y, z };
}

/** Unique orbit paths for guide rings */
export function orbitGuideRadii(): { rx: number; rz: number }[] {
  const seen = new Set<string>();
  const out: { rx: number; rz: number }[] = [];
  for (const g of NAVAGRAHA) {
    const key = `${g.orbitRadiusX}:${g.orbitRadiusZ}`;
    if (!seen.has(key)) {
      seen.add(key);
      out.push({ rx: g.orbitRadiusX, rz: g.orbitRadiusZ });
    }
  }
  return out.sort((a, b) => a.rx - b.rx);
}
