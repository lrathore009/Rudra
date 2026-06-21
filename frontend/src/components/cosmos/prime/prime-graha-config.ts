/** Rudra Prime — graha panel layout & attributes matching preview mockup */

import type { GrahaId } from "../navagraha-config";

export interface PrimeGrahaPanel {
  id: GrahaId;
  attributes: string[];
  /** Screen position (%), tuned to rudra-prime-preview.png */
  position: { leftPct: number; topPct: number };
  align: "left" | "right";
  glow: string;
}

export const PRIME_DEFAULT_COUNSEL =
  "Be still. Command not the answer, but the silence before it. Ask, and counsel will arise from the void.";

export const PRIME_GRAHA_PANELS: PrimeGrahaPanel[] = [
  {
    id: "surya",
    attributes: ["Soul", "Authority", "Vitality", "Illumination", "Leadership"],
    position: { leftPct: 14, topPct: 22 },
    align: "left",
    glow: "#ff9933",
  },
  {
    id: "mangal",
    attributes: ["Courage", "Force", "Energy", "Discipline", "Protection"],
    position: { leftPct: 12, topPct: 38 },
    align: "left",
    glow: "#ee4422",
  },
  {
    id: "budha",
    attributes: ["Intellect", "Logic", "Communication", "Commerce"],
    position: { leftPct: 11, topPct: 52 },
    align: "left",
    glow: "#33cc88",
  },
  {
    id: "guru",
    attributes: ["Wisdom", "Expansion", "Dharma", "Knowledge", "Guidance"],
    position: { leftPct: 13, topPct: 66 },
    align: "left",
    glow: "#eebb55",
  },
  {
    id: "shukra",
    attributes: ["Love", "Beauty", "Harmony", "Luxury", "Creativity"],
    position: { leftPct: 86, topPct: 22 },
    align: "right",
    glow: "#ffc0d8",
  },
  {
    id: "chandra",
    attributes: ["Mind", "Emotions", "Intuition", "Reflection", "Nourishment"],
    position: { leftPct: 88, topPct: 36 },
    align: "right",
    glow: "#aaccee",
  },
  {
    id: "shani",
    attributes: ["Discipline", "Karma", "Endurance", "Justice", "Structure"],
    position: { leftPct: 87, topPct: 50 },
    align: "right",
    glow: "#7799bb",
  },
  {
    id: "rahu",
    attributes: ["Obsession", "Illusion", "Desire", "Innovation", "Foreign", "Unconventional"],
    position: { leftPct: 86, topPct: 64 },
    align: "right",
    glow: "#bb55ff",
  },
  {
    id: "ketu",
    attributes: ["Moksha", "Detachment", "Spirituality", "Insight", "Liberation"],
    position: { leftPct: 84, topPct: 78 },
    align: "right",
    glow: "#9999aa",
  },
];
