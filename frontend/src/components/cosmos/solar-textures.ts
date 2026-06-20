/** Solar System Scope texture paths (2K — web-optimized) */

export const TEXTURE_BASE = "/textures/planets";

export type SolarBody =
  | "mercury"
  | "venus"
  | "earth"
  | "mars"
  | "jupiter"
  | "saturn"
  | "uranus"
  | "neptune"
  | "moon";

export const SOLAR_TEXTURES: Record<SolarBody | "earthClouds" | "saturnRing" | "sun", string> = {
  mercury: `${TEXTURE_BASE}/2k_mercury.jpg`,
  venus: `${TEXTURE_BASE}/2k_venus_surface.jpg`,
  earth: `${TEXTURE_BASE}/2k_earth_daymap.jpg`,
  earthClouds: `${TEXTURE_BASE}/2k_earth_clouds.jpg`,
  mars: `${TEXTURE_BASE}/2k_mars.jpg`,
  jupiter: `${TEXTURE_BASE}/2k_jupiter.jpg`,
  saturn: `${TEXTURE_BASE}/2k_saturn.jpg`,
  saturnRing: `${TEXTURE_BASE}/2k_saturn_ring_alpha.png`,
  uranus: `${TEXTURE_BASE}/2k_uranus.jpg`,
  neptune: `${TEXTURE_BASE}/2k_neptune.jpg`,
  moon: `${TEXTURE_BASE}/2k_moon.jpg`,
  sun: `${TEXTURE_BASE}/2k_sun.jpg`,
};

/** All unique URLs for preloading */
export const ALL_SOLAR_TEXTURE_URLS = [
  SOLAR_TEXTURES.mercury,
  SOLAR_TEXTURES.venus,
  SOLAR_TEXTURES.earth,
  SOLAR_TEXTURES.earthClouds,
  SOLAR_TEXTURES.mars,
  SOLAR_TEXTURES.jupiter,
  SOLAR_TEXTURES.saturn,
  SOLAR_TEXTURES.saturnRing,
  SOLAR_TEXTURES.uranus,
  SOLAR_TEXTURES.neptune,
  SOLAR_TEXTURES.moon,
  SOLAR_TEXTURES.sun,
];

export function textureForBody(body: SolarBody): string {
  return SOLAR_TEXTURES[body];
}
