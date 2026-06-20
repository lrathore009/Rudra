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
  name: string;
  tag: string;
  /** Vedic symbol shown on label card */
  symbol: string;
  /** Cognitive domain subtitle */
  domain: string;
  agentType: string;
  orbitRadiusX: number;
  orbitRadiusZ: number;
  orbitLift: number;
  /** Orbit path accent color */
  orbitColor: string;
  speed: number;
  angle: number;
  size: number;
  axialTilt: number;
  hasRings?: boolean;
  appearance: {
    color: string;
    emissive: string;
    emissiveIntensity: number;
    metalness: number;
    roughness: number;
    clearcoat?: number;
  };
}

/** Layout tuned for front-view “celestial machine” — wide X, shallow Z */
export const NAVAGRAHA: Navagraha[] = [
  {
    id: "surya",
    name: "Surya",
    tag: "SUR",
    symbol: "☉",
    domain: "Leadership & Authority",
    agentType: "executive_assistant",
    orbitRadiusX: 10.5,
    orbitRadiusZ: 3.2,
    orbitLift: 2.4,
    orbitColor: "#ffaa33",
    speed: 0.14,
    angle: 0.4,
    size: 0.32,
    axialTilt: 0.1,
    appearance: { color: "#ffb840", emissive: "#ff8800", emissiveIntensity: 0.65, metalness: 0.35, roughness: 0.35 },
  },
  {
    id: "chandra",
    name: "Chandra",
    tag: "CHN",
    symbol: "☽",
    domain: "Mind & Emotions",
    agentType: "writing",
    orbitRadiusX: 9.2,
    orbitRadiusZ: 2.8,
    orbitLift: 2.0,
    orbitColor: "#aaccee",
    speed: 0.17,
    angle: 5.6,
    size: 0.26,
    axialTilt: 0.06,
    appearance: { color: "#d8e4f0", emissive: "#88aacc", emissiveIntensity: 0.4, metalness: 0.5, roughness: 0.25, clearcoat: 0.5 },
  },
  {
    id: "mangal",
    name: "Mangal",
    tag: "MAN",
    symbol: "♂",
    domain: "Energy & Action",
    agentType: "travel",
    orbitRadiusX: 9.8,
    orbitRadiusZ: 3.0,
    orbitLift: 0.6,
    orbitColor: "#ee4422",
    speed: 0.15,
    angle: 4.2,
    size: 0.24,
    axialTilt: 0.25,
    appearance: { color: "#cc3311", emissive: "#991100", emissiveIntensity: 0.35, metalness: 0.7, roughness: 0.3 },
  },
  {
    id: "budha",
    name: "Budha",
    tag: "BUD",
    symbol: "☿",
    domain: "Intellect & Knowledge",
    agentType: "presentation",
    orbitRadiusX: 8.8,
    orbitRadiusZ: 2.6,
    orbitLift: -0.8,
    orbitColor: "#44cc88",
    speed: 0.19,
    angle: 3.8,
    size: 0.23,
    axialTilt: 0.04,
    appearance: { color: "#33bb77", emissive: "#118855", emissiveIntensity: 0.45, metalness: 0.4, roughness: 0.35 },
  },
  {
    id: "guru",
    name: "Guru",
    tag: "GUR",
    symbol: "♃",
    domain: "Wisdom, Strategy & Prosperity",
    agentType: "research_analyst",
    orbitRadiusX: 11.5,
    orbitRadiusZ: 3.5,
    orbitLift: -1.2,
    orbitColor: "#ddaa44",
    speed: 0.11,
    angle: 5.0,
    size: 0.42,
    axialTilt: 0.08,
    appearance: { color: "#eebb55", emissive: "#cc8822", emissiveIntensity: 0.5, metalness: 0.3, roughness: 0.4 },
  },
  {
    id: "shukra",
    name: "Shukra",
    tag: "SHK",
    symbol: "♀",
    domain: "Love, Luxury & Experience",
    agentType: "luxury_analyst",
    orbitRadiusX: 10.8,
    orbitRadiusZ: 3.3,
    orbitLift: 2.2,
    orbitColor: "#ff88aa",
    speed: 0.13,
    angle: 1.2,
    size: 0.28,
    axialTilt: 0.78,
    appearance: { color: "#ffc0d8", emissive: "#dd6699", emissiveIntensity: 0.4, metalness: 0.25, roughness: 0.18, clearcoat: 0.85 },
  },
  {
    id: "shani",
    name: "Shani",
    tag: "SHA",
    symbol: "♄",
    domain: "Discipline & Systems",
    agentType: "operations",
    orbitRadiusX: 10.0,
    orbitRadiusZ: 3.0,
    orbitLift: -1.8,
    orbitColor: "#6688aa",
    speed: 0.1,
    angle: 0.0,
    size: 0.27,
    axialTilt: 0.47,
    hasRings: true,
    appearance: { color: "#2a2a38", emissive: "#334455", emissiveIntensity: 0.2, metalness: 0.65, roughness: 0.5 },
  },
  {
    id: "rahu",
    name: "Rahu",
    tag: "RAH",
    symbol: "☊",
    domain: "Innovation & Future",
    agentType: "concierge",
    orbitRadiusX: 9.5,
    orbitRadiusZ: 2.9,
    orbitLift: 2.6,
    orbitColor: "#aa44ff",
    speed: 0.16,
    angle: 4.8,
    size: 0.25,
    axialTilt: 0.15,
    appearance: { color: "#6622aa", emissive: "#9933ff", emissiveIntensity: 0.45, metalness: 0.5, roughness: 0.55 },
  },
  {
    id: "ketu",
    name: "Ketu",
    tag: "KET",
    symbol: "☋",
    domain: "Wisdom & Liberation",
    agentType: "knowledge_librarian",
    orbitRadiusX: 9.0,
    orbitRadiusZ: 2.7,
    orbitLift: 0.2,
    orbitColor: "#888899",
    speed: 0.18,
    angle: 1.8,
    size: 0.24,
    axialTilt: 0.12,
    appearance: { color: "#9999aa", emissive: "#666677", emissiveIntensity: 0.35, metalness: 0.45, roughness: 0.45 },
  },
];

export const SSS_TEXTURE_BASE = "/textures/planets";
export const SSS_STARS_MILKY_WAY = `${SSS_TEXTURE_BASE}/2k_stars_milky_way.jpg`;

export const THIRD_EYE_OFFSET = { x: 0, y: 0.15, z: 0.16 } as const;
export const TRISHUL_SCALE = 2.35;

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
  const y = graha.orbitLift + Math.sin(angle * 0.5) * 0.25;
  return { x, y, z };
}
