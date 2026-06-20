export type CosmicNavHandle = {
  resetView: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
};

export const COSMIC_DEFAULT_TARGET: [number, number, number] = [0, 0.2, 0];

export function cosmicDefaultCamera(variant: "main" | "login"): [number, number, number] {
  return variant === "login" ? [0, 0.6, 22] : [0, 0.8, 26];
}
