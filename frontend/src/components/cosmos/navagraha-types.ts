/** Navagraha type definitions (shared by config + orbit math) */

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

export type GrahaSurface = "default" | "corona" | "banded" | "hex" | "swirl";

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
  orbitInclination: number;
  orbitAscending: number;
  rimAngle: number;
  screenLabel: { leftPct: number; topPct: number };
  labelOffsetX: number;
  labelOffsetY: number;
  speed: number;
  angle: number;
  size: number;
  axialTilt: number;
  surface: GrahaSurface;
  texture?: string;
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
