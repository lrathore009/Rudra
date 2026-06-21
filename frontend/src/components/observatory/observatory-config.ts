import type { GrahaId } from "@/components/cosmos/navagraha-types";

export interface ObservatoryInstrument {
  num: string;
  id: GrahaId;
  name: string;
  role: string;
  agentType: string;
  /** Small planet texture or null for nodes */
  texture?: string;
  nodeColor: string;
  metric: number;
}

const T = "/textures/planets";

/** Clock-dial order matching reference mockup (01 top → clockwise) */
export const OBSERVATORY_INSTRUMENTS: ObservatoryInstrument[] = [
  {
    num: "01",
    id: "surya",
    name: "SURYA",
    role: "Executive",
    agentType: "executive_assistant",
    texture: `${T}/2k_sun.jpg`,
    nodeColor: "#e8a030",
    metric: 94,
  },
  {
    num: "02",
    id: "chandra",
    name: "CHANDRA",
    role: "Writing",
    agentType: "writing",
    texture: `${T}/2k_moon.jpg`,
    nodeColor: "#a8b8c8",
    metric: 91,
  },
  {
    num: "03",
    id: "mangal",
    name: "MANGAL",
    role: "Travel",
    agentType: "travel",
    texture: `${T}/2k_mars.jpg`,
    nodeColor: "#c04030",
    metric: 89,
  },
  {
    num: "04",
    id: "budha",
    name: "BUDHA",
    role: "Presentation",
    agentType: "presentation",
    texture: `${T}/2k_mercury.jpg`,
    nodeColor: "#8c8b8a",
    metric: 92,
  },
  {
    num: "05",
    id: "guru",
    name: "GURU",
    role: "Research",
    agentType: "research_analyst",
    texture: `${T}/2k_jupiter.jpg`,
    nodeColor: "#c88b3a",
    metric: 95,
  },
  {
    num: "06",
    id: "shukra",
    name: "SHUKRA",
    role: "Luxury",
    agentType: "luxury_analyst",
    texture: `${T}/2k_venus_surface.jpg`,
    nodeColor: "#c890a8",
    metric: 88,
  },
  {
    num: "07",
    id: "shani",
    name: "SHANI",
    role: "Operations",
    agentType: "operations",
    texture: `${T}/2k_saturn.jpg`,
    nodeColor: "#607890",
    metric: 93,
  },
  {
    num: "08",
    id: "rahu",
    name: "RAHU",
    role: "Concierge",
    agentType: "concierge",
    nodeColor: "#8868b0",
    metric: 90,
  },
  {
    num: "09",
    id: "ketu",
    name: "KETU",
    role: "Archive",
    agentType: "knowledge_librarian",
    nodeColor: "#808890",
    metric: 91,
  },
];

export function instrumentByGraha(id?: GrahaId): ObservatoryInstrument | undefined {
  if (!id) return undefined;
  return OBSERVATORY_INSTRUMENTS.find((i) => i.id === id);
}

export function instrumentByAgent(agentType?: string): ObservatoryInstrument | undefined {
  if (!agentType) return undefined;
  return OBSERVATORY_INSTRUMENTS.find((i) => i.agentType === agentType);
}

/** Dial node positions — index 0 = 01 at top, clockwise */
export function dialNodePosition(index: number, cx: number, cy: number, r: number) {
  const deg = -90 + index * 40;
  const rad = (deg * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad), deg };
}

export const OBSERVATORY_OVERALL_METRIC = 92;
