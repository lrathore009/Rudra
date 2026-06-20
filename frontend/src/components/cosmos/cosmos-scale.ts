/**
 * Single scale authority — Trishul is the cosmic anchor; planets orbit around it.
 * All sizes and radii derive from TRISHUL_SCALE so the scene stays proportional.
 */

/** Trishul mesh scale — as large as the camera orbit allows */
export const TRISHUL_SCALE = 3.6;

/** Y offset inside TrishulDamru3D group — prong junction sits at world origin */
export const TRISHUL_PIVOT_Y = -1.05;

/** Sun corona radius (halo behind trishul, not a competing sphere) */
export const SUN_RADIUS = TRISHUL_SCALE * 0.38;

/** Planet size multiplier applied on top of per-body relative sizes */
export const PLANET_SIZE_FACTOR = TRISHUL_SCALE * 0.028;

/** Orbit radii — must clear the trishul silhouette (~TRISHUL_SCALE * 2.2) */
export const ORBIT_RADII = {
  mercury: TRISHUL_SCALE * 3.4,
  venus: TRISHUL_SCALE * 3.9,
  earth: TRISHUL_SCALE * 4.3,
  moon: TRISHUL_SCALE * 4.55,
  mars: TRISHUL_SCALE * 4.9,
  jupiter: TRISHUL_SCALE * 6.2,
  saturn: TRISHUL_SCALE * 7.0,
  uranus: TRISHUL_SCALE * 7.7,
  neptune: TRISHUL_SCALE * 8.4,
} as const;

/** Relative body diameters (Earth ≈ 1.0) before PLANET_SIZE_FACTOR */
export const BODY_SIZE: Record<string, number> = {
  mercury: 0.38,
  venus: 0.95,
  earth: 1.0,
  moon: 0.27,
  mars: 0.53,
  jupiter: 2.2,
  saturn: 1.85,
  uranus: 1.15,
  neptune: 1.1,
};

export function planetWorldSize(body: string): number {
  return (BODY_SIZE[body] ?? 1) * PLANET_SIZE_FACTOR;
}

export const ORBIT_RING_LIST = Object.values(ORBIT_RADII);

/** Camera / controls tuned to trishul + outer Neptune orbit */
export const CAMERA = {
  position: [0, TRISHUL_SCALE * 0.55, TRISHUL_SCALE * 7.2] as [number, number, number],
  fov: 48,
  target: [0, TRISHUL_SCALE * 0.15, 0] as [number, number, number],
  minDistance: TRISHUL_SCALE * 2.8,
  maxDistance: TRISHUL_SCALE * 11,
};

/** Lightning originates from center blade tip (local mesh space) */
export const BLADE_TIP_LOCAL_Y = 2.94;
