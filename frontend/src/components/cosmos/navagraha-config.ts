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
  symbol: string;
  domain: string;
  agentType: string;
  orbitRadiusX: number;
  orbitRadiusZ: number;
  orbitLift: number;
  orbitColor: string;
  /** Label offset away from Trishula (local space) */
  labelOffsetX: number;
  labelOffsetY: number;
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

/**
 * Fixed layout matching sovereign reference — spread around Trishula.
 * Angles place each Graha at a distinct quadrant; slow revolution only.
 */
export const NAVAGRAHA: Navagraha[] = [
  {
    id: "rahu",
    name: "Rahu",
    tag: "RAH",
    symbol: "☊",
    domain: "Innovation & Future",
    agentType: "concierge",
    orbitRadiusX: 11.0,
    orbitRadiusZ: 4.2,
    orbitLift: 2.8,
    orbitColor: "#bb55ff",
    labelOffsetX: -0.4,
    labelOffsetY: 0.9,
    speed: 0.06,
    angle: 2.35,
    size: 0.38,
    axialTilt: 0.15,
    appearance: { color: "#7722cc", emissive: "#aa44ff", emissiveIntensity: 0.55, metalness: 0.45, roughness: 0.5 },
  },
  {
    id: "chandra",
    name: "Chandra",
    tag: "CHN",
    symbol: "☽",
    domain: "Mind & Emotions",
    agentType: "writing",
    orbitRadiusX: 10.0,
    orbitRadiusZ: 3.8,
    orbitLift: 2.2,
    orbitColor: "#aaccee",
    labelOffsetX: -0.5,
    labelOffsetY: 0.85,
    speed: 0.07,
    angle: 2.85,
    size: 0.36,
    axialTilt: 0.06,
    appearance: { color: "#d8e4f0", emissive: "#99bbdd", emissiveIntensity: 0.45, metalness: 0.5, roughness: 0.22, clearcoat: 0.55 },
  },
  {
    id: "surya",
    name: "Surya",
    tag: "SUR",
    symbol: "☉",
    domain: "Leadership & Authority",
    agentType: "executive_assistant",
    orbitRadiusX: 11.5,
    orbitRadiusZ: 4.0,
    orbitLift: 2.5,
    orbitColor: "#ffaa33",
    labelOffsetX: 0.45,
    labelOffsetY: 0.9,
    speed: 0.06,
    angle: 0.55,
    size: 0.44,
    axialTilt: 0.1,
    appearance: { color: "#ffb840", emissive: "#ff8800", emissiveIntensity: 0.75, metalness: 0.35, roughness: 0.32 },
  },
  {
    id: "shukra",
    name: "Shukra",
    tag: "SHK",
    symbol: "♀",
    domain: "Love, Luxury & Experience",
    agentType: "luxury_analyst",
    orbitRadiusX: 11.2,
    orbitRadiusZ: 4.1,
    orbitLift: 2.6,
    orbitColor: "#ff77aa",
    labelOffsetX: 0.5,
    labelOffsetY: 0.85,
    speed: 0.065,
    angle: 1.05,
    size: 0.4,
    axialTilt: 0.78,
    appearance: { color: "#ffc0d8", emissive: "#ee5599", emissiveIntensity: 0.5, metalness: 0.25, roughness: 0.16, clearcoat: 0.9 },
  },
  {
    id: "ketu",
    name: "Ketu",
    tag: "KET",
    symbol: "☋",
    domain: "Wisdom & Liberation",
    agentType: "knowledge_librarian",
    orbitRadiusX: 10.5,
    orbitRadiusZ: 3.9,
    orbitLift: 0.5,
    orbitColor: "#9999aa",
    labelOffsetX: 0.55,
    labelOffsetY: 0.75,
    speed: 0.07,
    angle: 0.15,
    size: 0.36,
    axialTilt: 0.12,
    appearance: { color: "#aaaabb", emissive: "#777788", emissiveIntensity: 0.4, metalness: 0.45, roughness: 0.42 },
  },
  {
    id: "guru",
    name: "Guru",
    tag: "GUR",
    symbol: "♃",
    domain: "Wisdom, Strategy & Prosperity",
    agentType: "research_analyst",
    orbitRadiusX: 12.0,
    orbitRadiusZ: 4.3,
    orbitLift: -1.5,
    orbitColor: "#ddaa44",
    labelOffsetX: 0.5,
    labelOffsetY: -0.85,
    speed: 0.05,
    angle: 5.55,
    size: 0.52,
    axialTilt: 0.08,
    appearance: { color: "#eebb55", emissive: "#cc8822", emissiveIntensity: 0.55, metalness: 0.3, roughness: 0.38 },
  },
  {
    id: "shani",
    name: "Shani",
    tag: "SHA",
    symbol: "♄",
    domain: "Discipline & Systems",
    agentType: "operations",
    orbitRadiusX: 10.8,
    orbitRadiusZ: 3.7,
    orbitLift: -2.2,
    orbitColor: "#7799bb",
    labelOffsetX: 0,
    labelOffsetY: -0.95,
    speed: 0.05,
    angle: 4.75,
    size: 0.4,
    axialTilt: 0.47,
    hasRings: true,
    appearance: { color: "#3a3a48", emissive: "#445566", emissiveIntensity: 0.25, metalness: 0.7, roughness: 0.45 },
  },
  {
    id: "budha",
    name: "Budha",
    tag: "BUD",
    symbol: "☿",
    domain: "Intellect & Knowledge",
    agentType: "presentation",
    orbitRadiusX: 10.2,
    orbitRadiusZ: 3.6,
    orbitLift: -1.0,
    orbitColor: "#44dd99",
    labelOffsetX: -0.55,
    labelOffsetY: -0.8,
    speed: 0.075,
    angle: 3.65,
    size: 0.37,
    axialTilt: 0.04,
    appearance: { color: "#33cc88", emissive: "#118855", emissiveIntensity: 0.5, metalness: 0.4, roughness: 0.32 },
  },
  {
    id: "mangal",
    name: "Mangal",
    tag: "MAN",
    symbol: "♂",
    domain: "Energy & Action",
    agentType: "travel",
    orbitRadiusX: 10.6,
    orbitRadiusZ: 3.8,
    orbitLift: 0.3,
    orbitColor: "#ee4422",
    labelOffsetX: -0.55,
    labelOffsetY: 0.7,
    speed: 0.07,
    angle: 3.15,
    size: 0.38,
    axialTilt: 0.25,
    appearance: { color: "#dd3311", emissive: "#aa1100", emissiveIntensity: 0.45, metalness: 0.72, roughness: 0.28 },
  },
];

export const SSS_TEXTURE_BASE = "/textures/planets";
export const SSS_STARS_MILKY_WAY = `${SSS_TEXTURE_BASE}/2k_stars_milky_way.jpg`;

export const THIRD_EYE_OFFSET = { x: 0, y: 0.15, z: 0.16 } as const;
export const TRISHUL_SCALE = 2.9;

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
  const y = graha.orbitLift + Math.sin(angle * 0.5) * 0.15;
  return { x, y, z };
}
